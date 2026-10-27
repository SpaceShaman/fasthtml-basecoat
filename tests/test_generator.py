import base64
import hashlib
import io
import json
import shutil
import tarfile
from pathlib import Path
from urllib.error import HTTPError

import pytest

from scripts.generate import (
    download_archive,
    download_sources,
    generate,
    parse_components,
)

FIXTURES = Path(__file__).parent / "fixtures/upstream"


@pytest.fixture
def upstream(tmp_path):
    source = tmp_path / "source"
    package = tmp_path / "npm"
    shutil.copytree(FIXTURES / "components", source / "src/css/components")
    shutil.copytree(FIXTURES / "styles", source / "src/css/styles")
    shutil.copytree(FIXTURES / "docs", source / "site/src/docs/components")
    (source / "package.json").write_text('{"version": "1.0.2"}')
    (package / "dist/js").mkdir(parents=True)
    (package / "package.json").write_text('{"version": "1.0.2"}')
    for style in ("vega", "nova"):
        (package / "dist" / f"basecoat-{style}.bundle.css").write_text(
            ".btn { color: red; }"
        )
    (package / "dist/js/all.min.js").write_text("window.basecoat = {};")
    (package / "LICENSE.md").write_text("MIT")
    return source, package


def test_generation_is_repeatable_and_contains_local_assets(upstream, tmp_path):
    output = tmp_path / "project/src/fasthtml_basecoat"
    report = generate(*upstream, destination=output)
    original = {
        path.relative_to(output): path.read_bytes()
        for path in output.rglob("*")
        if path.is_file()
    }
    assert report["components"] == ["Button", "Card", "CardAction", "Switch", "Tabs"]
    assert report["skipped"] == []
    assert (
        (output / "assets/css/nova.css").read_text()
        == '@import "tailwindcss";\n@import "./basecoat-nova.bundle.css";\n@source "../../helpers.py";\n'
    )
    assert (output / "assets/js/all.min.js").is_file()
    assert (output.parents[1] / "BASECOAT-LICENSE").read_text() == "MIT"
    assert generate(*upstream, destination=output) == report
    assert original == {
        path.relative_to(output): path.read_bytes()
        for path in output.rglob("*")
        if path.is_file()
    }


def test_generation_rejects_mismatched_versions(upstream, tmp_path):
    source, package = upstream
    (package / "package.json").write_text('{"version": "2.0.0"}')
    output = tmp_path / "project/src/fasthtml_basecoat"
    with pytest.raises(ValueError, match="same version"):
        generate(source, package, destination=output)
    assert not output.exists()


def test_disappearing_components_stop_generation_before_writing(upstream, tmp_path):
    output = tmp_path / "project/src/fasthtml_basecoat"
    with pytest.raises(ValueError, match="disappeared"):
        generate(*upstream, destination=output, previous=["MissingComponent"])
    assert not output.exists()


def test_missing_sources_do_not_generate_an_empty_package(tmp_path):
    with pytest.raises(ValueError, match="No components"):
        parse_components(tmp_path)


def test_unsupported_documentation_is_reported(upstream):
    source, _ = upstream
    (source / "site/src/docs/components/unknown.mdx").write_text(
        "# Unknown\nNo component structure."
    )
    _, skipped = parse_components(source)
    assert skipped == ["unknown"]


def test_chart_is_not_exposed_without_its_javascript_integration(upstream):
    source, _ = upstream
    (source / "src/css/components/chart.css").write_text(".chart { color: red; }")
    (source / "site/src/docs/components/chart.mdx").write_text(
        '## HTML structure\n<dl><dt><code>&lt;div class="chart"&gt;</code></dt><dd>Chart.</dd></dl>'
    )
    components, skipped = parse_components(source)
    assert "chart" in skipped
    assert "Chart" not in {item.name for item in components}


def test_npm_integrity_is_checked_before_extraction(tmp_path, monkeypatch):
    content = io.BytesIO()
    with tarfile.open(fileobj=content, mode="w:gz") as archive:
        data = json.dumps({"version": "1.0.2"}).encode()
        member = tarfile.TarInfo("package/package.json")
        member.size = len(data)
        archive.addfile(member, io.BytesIO(data))
    raw = content.getvalue()
    monkeypatch.setattr(
        "scripts.generate.urlopen", lambda *args, **kwargs: io.BytesIO(raw)
    )
    destination = tmp_path / "invalid"
    with pytest.raises(ValueError, match="Integrity"):
        download_archive(
            "https://example.invalid/package.tgz",
            destination,
            "sha512-AAAA",
        )
    assert not destination.exists()
    integrity = "sha512-" + base64.b64encode(hashlib.sha512(raw).digest()).decode()
    root = download_archive(
        "https://example.invalid/package.tgz", tmp_path / "valid", integrity
    )
    assert json.loads((root / "package.json").read_text())["version"] == "1.0.2"


@pytest.mark.parametrize("tag", ["1.0.2", "v1.0.2"])
def test_sources_are_downloaded_only_from_the_matching_version_tag(
    tmp_path, monkeypatch, tag
):
    requests = []

    def download(url, destination):
        requests.append(url)
        if url.endswith("/" + tag):
            return tmp_path
        raise HTTPError(url, 404, "Not found", None, None)

    monkeypatch.setattr("scripts.generate.download_archive", download)
    assert download_sources("1.0.2", tmp_path) == tmp_path
    assert requests[-1].endswith("/" + tag)
    assert all(url.rsplit("/", 1)[-1] in {"1.0.2", "v1.0.2"} for url in requests)


def test_missing_matching_source_tag_stops_generation(tmp_path, monkeypatch):
    def download(url, destination):
        raise HTTPError(url, 404, "Not found", None, None)

    monkeypatch.setattr("scripts.generate.download_archive", download)
    with pytest.raises(ValueError, match="No Basecoat GitHub tag"):
        download_sources("1.0.2", tmp_path)

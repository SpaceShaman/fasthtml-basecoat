import io
import json
import tomllib
from pathlib import Path
from urllib.error import HTTPError

import pytest

from scripts import check_release


@pytest.mark.parametrize("state", ["new", "post", "published", "partial"])
def test_npm_controls_versions_and_only_missing_releases_are_published(
    tmp_path, monkeypatch, state
):
    monkeypatch.chdir(tmp_path)
    current = {"new": "1.0.0", "post": "1.1.0.post1"}.get(state, "1.1.0")
    Path("pyproject.toml").write_text(f'[project]\nversion = "{current}"\n')
    output = tmp_path / "output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    requests = []
    commands = []

    def response(url, **kwargs):
        requests.append(url)
        if "registry.npmjs.org" in url:
            return io.BytesIO(b'{"version": "1.1.0"}')
        if state in {"new", "post"}:
            raise HTTPError(url, 404, "Not found", None, None)
        names = ["fasthtml_basecoatui-1.1.0.tar.gz"]
        if state == "published":
            names.append("fasthtml_basecoatui-1.1.0-py3-none-any.whl")
        return io.BytesIO(
            json.dumps({"urls": [{"filename": name} for name in names]}).encode()
        )

    def update_version(command, **kwargs):
        commands.append(command)
        Path("pyproject.toml").write_text(f'[project]\nversion = "{command[2]}"\n')

    monkeypatch.setattr(check_release, "urlopen", response)
    monkeypatch.setattr(check_release.subprocess, "run", update_version)
    check_release.main()
    expected = "1.1.0.post1" if state == "post" else "1.1.0"
    assert (
        tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
        == expected
    )
    assert dict(line.split("=", 1) for line in output.read_text().splitlines()) == {
        "version": expected,
        "release": str(state != "published").lower(),
    }
    assert bool(commands) == (state == "new")
    assert requests[0] == "https://registry.npmjs.org/basecoat-css/latest"
    assert requests[1] == f"https://pypi.org/pypi/fasthtml-basecoatui/{expected}/json"
    assert not any("github" in url for url in requests)


def test_prerelease_npm_latest_is_rejected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("pyproject.toml").write_text('[project]\nversion = "1.1.0"\n')
    monkeypatch.setattr(
        check_release,
        "urlopen",
        lambda *a, **kw: io.BytesIO(b'{"version":"1.2.0-beta.1"}'),
    )
    with pytest.raises(ValueError, match="stable npm"):
        check_release.main()

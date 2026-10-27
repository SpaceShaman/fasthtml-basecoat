import argparse
import base64
import hashlib
import io
import json
import shutil
import tarfile
import tempfile
import tomllib
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .parser import parse_component, parse_css
from .render import HELPER_NAMES, HELPERS, render_components, render_init

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src/fasthtml_basecoat"


def read_version(root):
    return json.loads((root / "package.json").read_text(encoding="utf-8"))["version"]


def download_archive(url, destination, integrity=None):
    request = Request(url, headers={"User-Agent": "fasthtml-basecoatui"})
    with urlopen(request, timeout=60) as response:
        content = response.read()
    if integrity:
        algorithm, expected = integrity.split("-", 1)
        if hashlib.new(algorithm, content).digest() != base64.b64decode(expected):
            raise ValueError(f"Integrity mismatch for {url}")
    with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as archive:
        archive.extractall(destination, filter="data")
    (root,) = destination.iterdir()
    return root


def download_sources(version, directory):
    for tag in (version, f"v{version}"):
        try:
            return download_archive(
                f"https://api.github.com/repos/hunvreus/basecoat/tarball/{tag}",
                directory,
            )
        except HTTPError as error:
            if error.code != 404:
                raise
    raise ValueError(f"No Basecoat GitHub tag matches npm version {version}")


def parse_components(source):
    files = sorted((source / "src/css/components").glob("*.css"))
    files += sorted((source / "src/css/styles").glob("*.css"))
    css = parse_css("\n".join(path.read_text(encoding="utf-8") for path in files))
    components = {}
    skipped = []
    docs = sorted((source / "site/src/docs/components").glob("*.mdx"))
    for doc in docs:
        if doc.stem in HELPERS or doc.stem == "tooltip":
            continue
        if doc.stem == "chart":
            skipped.append(doc.stem)
            continue
        items = parse_component(doc.read_text(encoding="utf-8"), css, slug=doc.stem)
        if not items:
            skipped.append(doc.stem)
        for item in items:
            if item.name in components and components[item.name] != item:
                raise ValueError(f"Conflicting component: {item.name}")
            components[item.name] = item
    if not components:
        raise ValueError("No components found; check the Basecoat source directory")
    return sorted(components.values(), key=lambda item: item.name), skipped


def generate(source, package, destination=PACKAGE, previous=()):
    version = read_version(package)
    if read_version(source) != version:
        raise ValueError("GitHub sources and npm package must have the same version")
    components, skipped = parse_components(source)
    missing = set(previous) - {item.name for item in components}
    if missing:
        raise ValueError(
            f"Previously generated components disappeared: {sorted(missing)}"
        )
    styles = tuple(
        path.stem for path in sorted((source / "src/css/styles").glob("*.css"))
    )
    if "vega" not in styles:
        raise ValueError("Missing default Vega style")
    assets = destination / "assets"
    required = [package / "dist" / f"basecoat-{style}.bundle.css" for style in styles]
    required += [package / "dist/js/all.min.js", package / "LICENSE.md"]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    if assets.exists():
        shutil.rmtree(assets)
    (assets / "css").mkdir(parents=True)
    (assets / "js").mkdir()
    for style in styles:
        filename = f"basecoat-{style}.bundle.css"
        shutil.copyfile(package / "dist" / filename, assets / "css" / filename)
        (assets / "css" / f"{style}.css").write_text(
            f'@import "tailwindcss";\n@import "./{filename}";\n@source "../../helpers.py";\n',
            encoding="utf-8",
        )
    shutil.copyfile(package / "dist/js/all.min.js", assets / "js/all.min.js")
    shutil.copyfile(package / "LICENSE.md", destination.parents[1] / "BASECOAT-LICENSE")
    (destination / "components.py").write_text(
        render_components(components, version=version, styles=styles), encoding="utf-8"
    )
    (destination / "__init__.py").write_text(render_init(components), encoding="utf-8")
    report = {
        "version": version,
        "styles": list(styles),
        "components": [item.name for item in components],
        "helpers": HELPER_NAMES,
        "attributes": {"tooltip": "data-tooltip"},
        "skipped": skipped,
    }
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Generate components and bundle Basecoat assets"
    )
    parser.add_argument("--source", type=Path, help="Local Basecoat GitHub checkout")
    parser.add_argument(
        "--package", type=Path, help="Extracted basecoat-css npm package"
    )
    args = parser.parse_args()
    if (args.source is None) != (args.package is None):
        parser.error("--source and --package must be supplied together")
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"][
        "version"
    ].split(".post")[0]
    report_file = ROOT / "generation.json"
    previous = json.loads(report_file.read_text()) if report_file.exists() else {}
    with tempfile.TemporaryDirectory() as temporary:
        if args.source is not None:
            source, package = args.source.resolve(), args.package.resolve()
        else:
            with urlopen(
                f"https://registry.npmjs.org/basecoat-css/{version}", timeout=30
            ) as response:
                metadata = json.load(response)
            package = download_archive(
                metadata["dist"]["tarball"],
                Path(temporary) / "npm",
                metadata["dist"]["integrity"],
            )
            source = download_sources(version, Path(temporary) / "github")
        if read_version(package) != version:
            raise ValueError(
                f"Expected Basecoat {version}, got {read_version(package)}"
            )
        report = generate(source, package, previous=previous.get("components", ()))
    report_file.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(report['components'])} components for Basecoat {version}")
    print(f"Included {len(report['helpers'])} composed helpers")
    for slug in report["skipped"]:
        print(f"Skipped: {slug}")


if __name__ == "__main__":
    main()

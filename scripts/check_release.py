import json
import os
import re
import subprocess
import tomllib
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen


def published_files(version):
    try:
        with urlopen(
            f"https://pypi.org/pypi/fasthtml-basecoatui/{version}/json", timeout=30
        ) as response:
            return {item["filename"] for item in json.load(response)["urls"]}
    except HTTPError as error:
        if error.code != 404:
            raise
        return set()


def main():
    current = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
    with urlopen(
        "https://registry.npmjs.org/basecoat-css/latest", timeout=30
    ) as response:
        latest = json.load(response)["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", latest):
        raise ValueError(f"Expected stable npm version, got {latest!r}")
    if tuple(map(int, latest.split("."))) > tuple(
        map(int, current.split(".post")[0].split("."))
    ):
        subprocess.run(["uv", "version", latest, "--frozen", "--no-sync"], check=True)
        current = latest
    expected = {
        f"fasthtml_basecoatui-{current}-py3-none-any.whl",
        f"fasthtml_basecoatui-{current}.tar.gz",
    }
    release = not expected <= published_files(current)
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write(f"version={current}\nrelease={str(release).lower()}\n")


if __name__ == "__main__":
    main()

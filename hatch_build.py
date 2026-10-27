import json
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if version == "editable":
            return
        root = Path(self.root)
        report = json.loads((root / "generation.json").read_text(encoding="utf-8"))
        expected = self.metadata.version.split(".post")[0]
        if report["version"] != expected:
            raise ValueError("Regenerate components for the current Basecoat version")
        assets = root / "src/fasthtml_basecoat/assets"
        required = [assets / "js/all.min.js"]
        for style in report["styles"]:
            required.extend(
                (
                    assets / "css" / f"{style}.css",
                    assets / "css" / f"basecoat-{style}.bundle.css",
                )
            )
        if not all(path.is_file() for path in required):
            raise RuntimeError(
                "Missing Basecoat assets. Run: uv run --group dev python -m scripts.generate"
            )

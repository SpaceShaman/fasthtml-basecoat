from pathlib import Path

from fasthtml.common import Script

from .components import STYLES, Style

ASSETS = Path(__file__).parent / "assets"


def BasecoatInput(style: Style = "vega") -> Path:
    if style not in STYLES:
        raise ValueError(f"Unknown Basecoat style: {style!r}; choose from {STYLES}")
    return ASSETS / "css" / f"{style}.css"


def BasecoatJS(**attrs):
    return Script((ASSETS / "js" / "all.min.js").read_text(encoding="utf-8"), **attrs)

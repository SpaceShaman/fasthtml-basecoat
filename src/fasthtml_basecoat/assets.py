from pathlib import Path

from fasthtml.common import Script

from .components import STYLES, Style

ASSETS = Path(__file__).parent / "assets"
THEME_INIT = """(() => {
  let mode;
  try { mode = localStorage.getItem('themeMode'); } catch (_) {}
  const dark = mode === 'dark' || (mode !== 'light' && matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.classList.toggle('dark', dark);
})();
"""


def BasecoatInput(style: Style = "vega") -> Path:
    if style not in STYLES:
        raise ValueError(f"Unknown Basecoat style: {style!r}; choose from {STYLES}")
    return ASSETS / "css" / f"{style}.css"


def BasecoatJS(**attrs):
    code = THEME_INIT + (ASSETS / "js" / "all.min.js").read_text(encoding="utf-8")
    return Script(code, **attrs)

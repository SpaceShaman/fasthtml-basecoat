import json
import tomllib
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from fasthtml.common import FastHTML, StaticImmutable, to_xml
from fasthtml_tailwindcss import TailwindHead
from fasthtml_tailwindcss.build import build
from starlette.testclient import TestClient

from fasthtml_basecoat import (
    BASECOAT_VERSION,
    STYLES,
    BasecoatInput,
    BasecoatJS,
    Button,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("style", STYLES)
def test_packaged_inputs_compile_with_automatic_application_scanning(
    style, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "main.py").write_text('classes = "p-7 bg-primary text-foreground"\n')
    head = TailwindHead(input=BasecoatInput(style))
    build(head._config)
    css = (tmp_path / "static/tailwind.css").read_text()
    assert ".p-7{" in css
    assert ".bg-primary{" in css
    assert ".text-foreground{" in css
    assert ".btn" in css


def test_javascript_is_bundled_inline_and_accepts_attributes():
    html = str(to_xml(BasecoatJS(nonce="test-nonce")))
    script = BeautifulSoup(html, "html.parser").script
    assert script["nonce"] == "test-nonce"
    assert "src" not in script.attrs
    assert "basecoat" in script.string
    assert html.count("</script>") == 1


def test_invalid_style_is_rejected():
    with pytest.raises(ValueError, match="Unknown Basecoat style"):
        BasecoatInput("invalid")


def test_generated_version_and_component_report_match_the_package():
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    report = json.loads((ROOT / "generation.json").read_text())
    assert BASECOAT_VERSION == version.split(".post")[0] == report["version"]
    assert tuple(report["styles"]) == STYLES


def test_application_serves_compiled_css_and_bundled_javascript(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    head = TailwindHead(input=BasecoatInput())
    build(head._config)
    app = FastHTML(sess_cls=None, hdrs=[head, BasecoatJS()])
    app.mount("/static", StaticImmutable(directory="static"), name="static")
    app.route("/")(lambda: Button("Save", variant="outline"))
    with TestClient(app) as browser:
        page = BeautifulSoup(browser.get("/").text, "html.parser")
        assert page.button["class"] == ["btn"]
        assert page.button["data-variant"] == "outline"
        link = page.select_one('link[href^="/static/tailwind.css"]')
        assert "?v=" in link["href"]
        response = browser.get(link["href"])
        assert response.status_code == 200
        assert ".btn" in response.text
        assert "immutable" in response.headers["cache-control"]
        assert any(
            "basecoat" in (script.string or "")
            for script in page.find_all("script", src=False)
        )

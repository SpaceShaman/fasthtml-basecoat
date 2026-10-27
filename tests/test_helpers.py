import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from fasthtml.common import Div, to_xml

import fasthtml_basecoat
from fasthtml_basecoat import (
    Button,
    Pagination,
    PaginationLink,
    ScrollArea,
    Separator,
    Spinner,
    ThemeSwitcher,
)


def element(node):
    return BeautifulSoup(str(to_xml(node)), "html.parser").find()


@pytest.mark.parametrize("orientation", ["horizontal", "vertical"])
def test_separator_orientation_and_accessibility(orientation):
    node = element(Separator(orientation=orientation, cls="my-4"))
    assert node.name == "hr"
    assert node["role"] == "separator"
    assert node["aria-orientation"] == orientation
    assert node["class"] == ["my-4"]
    decorative = element(Separator(orientation=orientation, decorative=True))
    assert decorative["role"] == "none"
    assert decorative["aria-hidden"] == "true"
    assert decorative["aria-orientation"] == orientation


def test_separator_rejects_invalid_orientation():
    with pytest.raises(ValueError, match="Invalid orientation"):
        Separator(orientation="diagonal")


def test_scroll_area_preserves_children_and_attributes():
    node = element(ScrollArea(Div("Content"), cls="h-72", id="history"))
    assert node["class"] == ["scrollbar", "overflow-auto", "h-72"]
    assert node["id"] == "history"
    assert node.div.string == "Content"


def test_pagination_markup_links_and_current_page():
    node = element(
        Pagination(
            PaginationLink("Previous", href="?page=1"),
            PaginationLink("2", href="?page=2", current=True, size="icon"),
            PaginationLink("Next", href="?page=3"),
            aria_label="Results pages",
            cls="mt-8",
        )
    )
    assert node.name == "nav"
    assert node["aria-label"] == "Results pages"
    items = node.ul.find_all("li", recursive=False)
    assert len(items) == 3
    assert [item.a["href"] for item in items] == ["?page=1", "?page=2", "?page=3"]
    assert items[1].a["aria-current"] == "page"
    assert items[1].a["data-variant"] == "outline"
    assert items[1].a["data-size"] == "icon"
    assert items[0].a["data-variant"] == "ghost"
    assert "aria-current" not in items[0].a.attrs


def test_spinner_svg_status_and_customization():
    node = element(Spinner(cls="size-6", aria_label="Saving"))
    assert node.name == "svg"
    assert node["role"] == "status"
    assert node["aria-label"] == "Saving"
    assert "animate-spin" in node["class"]
    assert "size-6" in node["class"]
    assert node.circle["stroke-dasharray"] == "42 14"


def test_theme_switcher_uses_basecoat_runtime_and_decorative_icons():
    node = element(
        ThemeSwitcher(variant="ghost", aria_label="Change appearance", cls="size-10")
    )
    assert node.name == "button"
    assert node["type"] == "button"
    assert node["aria-label"] == "Change appearance"
    assert node["data-variant"] == "ghost"
    assert node["onclick"] == "window.basecoat.theme.toggle()"
    assert len(node.find_all("svg")) == 2
    assert all(svg["aria-hidden"] == "true" for svg in node.find_all("svg"))
    assert node.select_one('span[class="hidden dark:block"]') is not None
    assert node.select_one('span[class="block dark:hidden"]') is not None


def test_tooltip_remains_an_attribute_on_any_component():
    node = element(Button("Save", data_tooltip="Save changes", data_side="bottom"))
    assert node["data-tooltip"] == "Save changes"
    assert node["data-side"] == "bottom"
    assert not hasattr(fasthtml_basecoat, "Tooltip")


def test_report_distinguishes_helpers_attributes_and_unsupported_chart():
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root / "generation.json").read_text())
    assert set(report["helpers"]) == {
        "Pagination",
        "PaginationLink",
        "ScrollArea",
        "Separator",
        "Spinner",
        "ThemeSwitcher",
    }
    assert set(report["helpers"]) <= set(fasthtml_basecoat.__all__)
    assert report["attributes"] == {"tooltip": "data-tooltip"}
    assert "chart" in report["skipped"]
    assert not set(report["skipped"]) & {
        "pagination",
        "scroll-area",
        "separator",
        "spinner",
        "theme-switcher",
        "tooltip",
    }

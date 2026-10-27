from typing import Literal

from fasthtml.common import Div, Li, Nav, Span, Ul
from fasthtml.components import ft_html
from fasthtml.svg import Circle, Svg
from fasthtml.svg import Path as SvgPath

from .components import Button, _option

__all__ = [
    "Pagination",
    "PaginationLink",
    "ScrollArea",
    "Separator",
    "Spinner",
    "ThemeSwitcher",
]


def Separator(
    *,
    orientation: Literal["horizontal", "vertical"] = "horizontal",
    decorative: bool = False,
    cls: str = "",
    **attrs,
):
    _option("orientation", orientation, ("horizontal", "vertical"))
    attrs.setdefault("role", "none" if decorative else "separator")
    attrs.setdefault("aria_orientation", orientation)
    if decorative:
        attrs.setdefault("aria_hidden", "true")
    return ft_html("hr", cls=cls, **attrs)


def ScrollArea(*children, cls: str = "", **attrs):
    return Div(*children, cls=f"scrollbar overflow-auto {cls}".strip(), **attrs)


def Pagination(*children, cls: str = "", **attrs):
    attrs.setdefault("role", "navigation")
    attrs.setdefault("aria_label", "Pagination")
    return Nav(
        Ul(*(Li(child) for child in children), cls="flex flex-row items-center gap-1"),
        cls=f"mx-auto flex w-full justify-center {cls}".strip(),
        **attrs,
    )


def PaginationLink(*children, href: str, current: bool = False, cls: str = "", **attrs):
    attrs.setdefault("tag", "a")
    attrs.setdefault("variant", "outline" if current else "ghost")
    if current:
        attrs.setdefault("aria_current", "page")
    return Button(*children, href=href, cls=cls, **attrs)


def _icon(*children, cls: str = "", **attrs):
    defaults = {
        "viewBox": "0 0 24 24",
        "width": 24,
        "height": 24,
        "fill": "none",
        "stroke": "currentColor",
        "stroke_width": 2,
        "stroke_linecap": "round",
        "stroke_linejoin": "round",
    }
    return Svg(*children, cls=cls, **(defaults | attrs))


def Spinner(*, cls: str = "", **attrs):
    attrs.setdefault("role", "status")
    attrs.setdefault("aria_label", "Loading")
    attrs.setdefault("width", 16)
    attrs.setdefault("height", 16)
    return _icon(
        Circle(cx=12, cy=12, r=9, stroke_dasharray="42 14"),
        cls=f"shrink-0 animate-spin {cls}".strip(),
        **attrs,
    )


def ThemeSwitcher(*, cls: str = "", **attrs):
    attrs.setdefault("type", "button")
    attrs.setdefault("variant", "outline")
    attrs.setdefault("size", "icon")
    attrs.setdefault("aria_label", "Toggle dark mode")
    attrs.setdefault("onclick", "window.basecoat.theme.toggle()")
    return Button(
        Span(
            _icon(
                Circle(cx=12, cy=12, r=4),
                SvgPath(
                    d="M12 2v2 M12 20v2 M2 12h2 M20 12h2 M5 5l1.4 1.4 M17.6 17.6 19 19 M5 19l1.4-1.4 M17.6 6.4 19 5"
                ),
                aria_hidden="true",
            ),
            cls="hidden dark:block",
        ),
        Span(
            _icon(
                SvgPath(d="M20 15.2A8 8 0 0 1 8.8 4 8 8 0 1 0 20 15.2Z"),
                aria_hidden="true",
            ),
            cls="block dark:hidden",
        ),
        cls=cls,
        **attrs,
    )

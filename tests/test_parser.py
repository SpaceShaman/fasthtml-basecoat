import ast
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from fastcore.xml import to_xml

from scripts.parser import Component, parse_component, parse_css
from scripts.render import render_components

UPSTREAM = Path(__file__).parent / "fixtures/upstream"


def parsed(slug):
    css = (UPSTREAM / "components" / f"{slug}.css").read_text()
    css += "\n" + "\n".join(
        path.read_text() for path in sorted((UPSTREAM / "styles").glob("*.css"))
    )
    return parse_component(
        (UPSTREAM / "docs" / f"{slug}.mdx").read_text(), parse_css(css), slug=slug
    )


def functions(components):
    source = render_components(components, version="1.0.2", styles=("nova", "vega"))
    ast.parse(source)
    namespace = {}
    exec(source, namespace)
    return namespace


@pytest.mark.parametrize(
    "slug,names",
    [
        ("button", ["Button"]),
        ("card", ["Card", "CardAction"]),
        ("tabs", ["Tabs"]),
        ("switch", ["Switch"]),
    ],
)
def test_original_sources_preserve_component_names(slug, names):
    assert [item.name for item in parsed(slug)] == names


def test_button_typed_options_and_html():
    (button,) = parsed("button")
    assert "data-icon" not in button.options
    assert button.options["data-variant"] == {
        "primary",
        "secondary",
        "outline",
        "ghost",
        "link",
        "destructive",
    }
    constructor = functions([button])["Button"]
    node = constructor(
        "Save <now>", variant="outline", size="sm", cls="w-full", hx_post="/save"
    )
    html = str(to_xml(node))
    element = BeautifulSoup(html, "html.parser").button
    assert element.attrs == {
        "class": ["btn", "w-full"],
        "data-variant": "outline",
        "data-size": "sm",
        "hx-post": "/save",
    }
    assert "Save &lt;now&gt;" in html
    with pytest.raises(ValueError, match="Invalid size"):
        constructor(size="huge")


def test_native_children_remain_native():
    from fasthtml.common import H2, Header, Section

    components = parsed("card")
    card = components[0]
    assert card.options == {"data-size": {"sm"}}
    node = functions(components)["Card"](
        Header(H2("Title")), Section("Content"), size="sm"
    )
    element = BeautifulSoup(str(to_xml(node)), "html.parser").div
    assert element.header.h2.string == "Title"
    assert element.section.string == "Content"


def test_tabs_does_not_inherit_child_options():
    (tabs,) = parsed("tabs")
    assert "data-variant" not in tabs.options


def test_switch_semantics():
    switch = functions(parsed("switch"))["Switch"]
    html = str(to_xml(switch(checked=True, size="sm")))
    element = BeautifulSoup(html, "html.parser").input
    assert element["type"] == "checkbox"
    assert element["role"] == "switch"
    assert element["data-size"] == "sm"
    assert element.has_attr("checked")
    assert "</input>" not in html


def test_nested_selectors_keep_options_on_their_owners():
    css = """@layer components {
      .widget[data-size="sm"] {
        &[data-variant="outline"] { color: red; }
        > nav[data-variant="child"] { &[data-side="left"] { color: red; } }
        &:has(svg[data-icon="start"]) { color: blue; }
      }
      .widget > nav[data-variant="other"] { color: red; }
      /* .fake[data-size="bad"] {} */
    }"""
    result = parse_css(css)
    assert result["widget"] == {"data-size": {"sm"}, "data-variant": {"outline"}}
    assert "fake" not in result


def test_pseudo_class_children_do_not_own_parent_options():
    result = parse_css('.widget:has(.child) { &[data-size="sm"] { color: red; } }')
    assert result["widget"] == {"data-size": {"sm"}}
    assert result["child"] == {}


def test_style_packs_supply_undocumented_variants():
    mdx = '## HTML structure\n<dl><dt><code>&lt;div class="widget"&gt;</code></dt><dd>A widget.</dd></dl>'
    css = parse_css(
        '.widget { color: red; } @layer components { .widget[data-size="compact"] { color: blue; }}'
    )
    assert parse_component(mdx, css, slug="widget")[0].options == {
        "data-size": {"compact"}
    }


def test_tag_override_and_arbitrary_attributes():
    button = functions(parsed("button"))["Button"]
    element = BeautifulSoup(
        str(to_xml(button("Go", tag="a", href="/next", aria_label="Next"))),
        "html.parser",
    ).a
    assert element["href"] == "/next"
    assert element["aria-label"] == "Next"


def test_rendering_is_deterministic_and_escapes_descriptions():
    first = Component(
        "Alpha", "div", "alpha", 'Triple """ quotes and \\ slashes\nUnicode: naïve café'
    )
    second = Component("Beta", "span", "beta", "Beta")
    kwargs = {"version": "1", "styles": ("vega",)}
    assert render_components([first, second], **kwargs) == render_components(
        [second, first], **kwargs
    )
    assert functions([first])["Alpha"].__doc__ == first.description
    with pytest.raises(ValueError, match="Duplicate"):
        render_components([first, first], **kwargs)
    with pytest.raises(ValueError, match="Invalid"):
        render_components([Component("Bad-name", "div", "bad", "")], **kwargs)

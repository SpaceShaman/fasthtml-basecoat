import re
from dataclasses import dataclass, field

import tinycss2
from bs4 import BeautifulSoup, Tag

ALIASES = {
    "button": {"btn"},
    "field": {"fieldset"},
    "native-select": {"select"},
    "radio-group": {"radio", "input"},
    "checkbox": {"input"},
    "switch": {"input"},
    "slider": {"input"},
}
ROOT_NAMES = {
    "native-select": "NativeSelect",
    "checkbox": "Checkbox",
    "switch": "Switch",
    "slider": "Slider",
    "radio-group": "Radio",
}
GROUP_RULES = {"layer", "media", "supports", "container", "scope"}
STRUCTURE = re.compile(
    r"^#{2,6}\s+HTML structure\s*\n(.*?)(?=^#{1,6}\s|\Z)", re.M | re.S | re.I
)
DATA_VALUE = re.compile(r"""data-([\w-]+)=["']([^"']+)["']""")


@dataclass
class Component:
    name: str
    tag: str
    css_class: str
    description: str
    options: dict[str, set[str]] = field(default_factory=dict)
    defaults: dict[str, str] = field(default_factory=dict)


def pascal(value):
    return "".join(part.capitalize() for part in value.split("-"))


def classes(tokens):
    for index, token in enumerate(tokens):
        if token.type == "function":
            yield from classes(token.arguments)
        if token.type != "literal" or token.value != ".":
            continue
        if index + 1 < len(tokens) and tokens[index + 1].type == "ident":
            yield tokens[index + 1].value


def selectors(tokens):
    group = []
    for token in tokens:
        if token.type == "literal" and token.value == ",":
            yield group
            group = []
        elif token.type != "comment":
            group.append(token)
    yield group


def boundary(token):
    return token.type == "whitespace" or (
        token.type == "literal" and token.value in {">", "+", "~"}
    )


def data_attribute(token):
    if token.type != "[] block":
        return None
    parts = [t for t in token.content if t.type not in {"whitespace", "comment"}]
    if len(parts) != 3:
        return None
    name, operator, value = parts
    if name.type != "ident" or not name.value.startswith("data-"):
        return None
    if operator.type != "literal" or operator.value != "=":
        return None
    if value.type not in {"string", "ident"}:
        return None
    return name.value, value.value


def selector_options(tokens, parents, result):
    owners = set()
    for index, token in enumerate(tokens):
        if boundary(token):
            owners.clear()
        elif token.type == "literal" and token.value == "&":
            owners.update(parents)
        elif token.type == "literal" and token.value == ".":
            owners.update(classes(tokens[index : index + 2]))
        elif attribute := data_attribute(token):
            name, value = attribute
            for owner in owners:
                result.setdefault(owner, {}).setdefault(name, set()).add(value)
    return owners


def parse_rules(rules, parents, result):
    for rule in rules:
        if rule.type == "error":
            raise ValueError(f"Invalid CSS: {rule.message}")
        if rule.type == "at-rule":
            if rule.content is not None and rule.lower_at_keyword in GROUP_RULES:
                parse_rules(
                    tinycss2.parse_blocks_contents(rule.content), parents, result
                )
            continue
        if rule.type != "qualified-rule":
            continue
        for name in classes(rule.prelude):
            result.setdefault(name, {})
        endings = set()
        for selector in selectors(rule.prelude):
            while selector and selector[-1].type == "whitespace":
                selector.pop()
            endings.update(selector_options(selector, parents, result))
        if rule.content is not None:
            parse_rules(tinycss2.parse_blocks_contents(rule.content), endings, result)


def parse_css(css):
    result = {}
    rules = tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)
    parse_rules(rules, set(), result)
    return result


def belongs(slug, css_class):
    return (
        css_class == slug
        or css_class.startswith(slug + "-")
        or css_class in ALIASES.get(slug, ())
    )


def element_description(dt):
    dd = dt.find_next_sibling("dd")
    if dd is None:
        return ""
    return " ".join(
        item.get_text(" ", strip=True) if isinstance(item, Tag) else str(item).strip()
        for item in dd.contents
        if getattr(item, "name", None) != "dl"
    ).strip()


def documented_options(dt):
    result = {}
    for sibling in dt.find_next_siblings("dt"):
        code = sibling.find("code")
        if code is None:
            continue
        text = code.get_text()
        if text.startswith("<"):
            break
        if match := DATA_VALUE.fullmatch(text):
            result.setdefault("data-" + match[1], set()).update(match[2].split("|"))
    return result


def component(element, css_class, slug, css, description="", options=None):
    name = ROOT_NAMES.get(slug, "Button" if css_class == "btn" else pascal(css_class))
    values = {key: set(value) for key, value in css[css_class].items()}
    for key, value in (options or {}).items():
        values.setdefault(key, set()).update(value)
    defaults = {key: element[key] for key in ("type", "role") if element.get(key)}
    return Component(
        name,
        element.name,
        css_class,
        description or f"Basecoat {name}.",
        values,
        defaults,
    )


def structure_components(section, css, slug):
    soup = BeautifulSoup(section, "html.parser")
    for dt in soup.find_all("dt"):
        code = dt.find("code")
        if code is None or not code.get_text().startswith("<"):
            continue
        element = BeautifulSoup(code.get_text(), "html.parser").find()
        if element is None:
            continue
        for css_class in element.get("class", []):
            if css_class in css and belongs(slug, css_class):
                yield component(
                    element,
                    css_class,
                    slug,
                    css,
                    element_description(dt),
                    documented_options(dt),
                )


def parse_component(mdx, css, *, slug):
    section = STRUCTURE.search(mdx)
    found = {}
    for item in structure_components(section[1] if section else "", css, slug):
        found.setdefault(item.name, item)
    examples = BeautifulSoup(mdx, "html.parser")
    for element in examples.find_all(class_=True):
        for css_class in element.get("class", []):
            if css_class not in css or not belongs(slug, css_class):
                continue
            if (
                section
                and css_class != slug
                and slug not in {"checkbox", "radio-group"}
            ):
                continue
            item = component(element, css_class, slug, css)
            found.setdefault(item.name, item)
    return sorted(found.values(), key=lambda item: item.name)

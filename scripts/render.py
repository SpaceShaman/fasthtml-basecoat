import keyword

from .parser import Component


def parameter(attribute):
    name = attribute.removeprefix("data-").replace("-", "_")
    if not name.isidentifier() or keyword.iskeyword(name):
        raise ValueError(f"Unsupported parameter: {attribute}")
    if name in {"cls", "tag", "children", "attrs"}:
        raise ValueError(f"Reserved parameter: {attribute}")
    return name


def render_component(item: Component):
    options = [
        (parameter(key), key, sorted(values))
        for key, values in sorted(item.options.items())
    ]
    lines = [f"def {item.name}(", "    *children,"]
    for name, _, values in options:
        literal = ", ".join(repr(value) for value in values)
        lines.append(f"    {name}: Literal[{literal}] | None = None,")
    lines += [
        '    cls: str = "",',
        f"    tag: str = {item.tag!r},",
        "    **attrs,",
        "):",
    ]
    lines.append(f"    {item.description!r}")
    for key, value in sorted(item.defaults.items()):
        lines.append(f"    attrs.setdefault({key!r}, {value!r})")
    for name, attribute, values in options:
        lines += [
            f"    if {name} is not None:",
            f"        attrs[{attribute!r}] = _option({name!r}, {name}, {tuple(values)!r})",
        ]
    lines += [
        f"    classes = ' '.join(filter(None, ({item.css_class!r}, cls)))",
        "    return ft_html(tag, *children, cls=classes, **attrs)",
    ]
    return "\n".join(lines)


def render_components(components, *, version, styles):
    names = [item.name for item in components]
    reserved = {"BASECOAT_VERSION", "STYLES", "Style", "BasecoatInput", "BasecoatJS"}
    if len(names) != len(set(names)):
        raise ValueError("Duplicate component name")
    for name in names:
        if not name.isidentifier() or keyword.iskeyword(name) or name in reserved:
            raise ValueError(f"Invalid component name: {name}")
    lines = [
        '"""Generated Basecoat components."""',
        "",
        "from typing import Literal",
        "",
        "from fasthtml.components import ft_html",
        "",
        f"BASECOAT_VERSION = {version!r}",
        f"STYLES = {tuple(styles)!r}",
        f"Style = Literal[{', '.join(repr(style) for style in styles)}]",
        "",
        "__all__ = [",
        *(f"    {name!r}," for name in sorted(names)),
        "]",
        "",
        "",
        "def _option(name: str, value: str, choices: tuple[str, ...]) -> str:",
        "    if value not in choices:",
        '        raise ValueError(f"Invalid {name}: {value!r}; choose from {choices}")',
        "    return value",
        "",
        "",
    ]
    source = "\n".join(lines)
    source += (
        "\n\n\n".join(
            render_component(item)
            for item in sorted(components, key=lambda item: item.name)
        )
        + "\n"
    )
    compile(source, "components.py", "exec")
    return source


def render_init(components):
    names = ["BASECOAT_VERSION", "STYLES"] + sorted(
        [item.name for item in components] + ["Style"]
    )
    lines = [
        "from .assets import BasecoatInput, BasecoatJS",
        "from .components import (",
        *(f"    {name}," for name in names),
        ")",
        "",
        "__all__ = [",
        *(f"    {name!r}," for name in sorted(names + ["BasecoatInput", "BasecoatJS"])),
        "]",
        "",
    ]
    return "\n".join(lines)

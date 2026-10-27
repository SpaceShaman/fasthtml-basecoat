# fasthtml-basecoatui

[![License](https://img.shields.io/github/license/SpaceShaman/fasthtml-basecoatui)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/fasthtml-basecoatui)](https://pypi.org/project/fasthtml-basecoatui/)
[![Python](https://img.shields.io/pypi/pyversions/fasthtml-basecoatui)](https://pypi.org/project/fasthtml-basecoatui/)
[![Release](https://img.shields.io/github/actions/workflow/status/SpaceShaman/fasthtml-basecoatui/release.yml?label=release)](https://github.com/SpaceShaman/fasthtml-basecoatui/actions/workflows/release.yml)
[![FastHTML](https://img.shields.io/badge/framework-FastHTML-7854F7)](https://github.com/AnswerDotAI/fasthtml)
[![Basecoat](https://img.shields.io/badge/UI-Basecoat-18181B)](https://basecoatui.com/)

Basecoat components and bundled assets for [FastHTML](https://github.com/AnswerDotAI/fasthtml).

Typed Python components generated from [Basecoat](https://basecoatui.com/), with local CSS and JavaScript. CSS builds and watch mode are provided by [fasthtml-tailwindcss](https://github.com/SpaceShaman/fasthtml-tailwindcss). No Node.js, npm, or CDN is needed in your application.

## Installation

- With uv:

  ```sh
  uv add fasthtml-basecoatui
  ```

- With pip:

  ```sh
  pip install fasthtml-basecoatui
  ```

For development and CSS builds, also install the Tailwind compiler:

```sh
uv add "fasthtml-tailwindcss[dev]"
```

Or `pip install "fasthtml-tailwindcss[dev]"`. Production only needs `fasthtml-basecoatui` and the generated CSS. Alpine Linux also requires `apk add --no-cache libstdc++ libgcc` when using the compiler.

## Usage

```python
from fasthtml.common import FastHTML, StaticImmutable
from fasthtml_tailwindcss import TailwindHead
from fasthtml_basecoat import BasecoatInput, BasecoatJS, Button

app = FastHTML(
    hdrs=[
        BasecoatJS(),
        TailwindHead(input=BasecoatInput("nova"), watch=True),
    ]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get():
    return Button("Save", variant="outline", size="sm", cls="w-full")
```

Run `uv run uvicorn main:app --reload`. For `app/main.py`, run `uv run --directory app uvicorn main:app --reload` from the project directory.

`TailwindHead` creates `static/`, writes CSS to `static/tailwind.css`, and adds a content-versioned stylesheet link for browser caching. Compilation starts on the first page render. The watcher rebuilds CSS as your classes change and survives server reloads; refresh the browser to see updates.

### Examples

Each file in [examples](examples) is a standalone application following Basecoat's HTML structure, with local CSS and JavaScript:

- [Contact form](examples/form.py) — fields, validation, and form submission.
- [Workspace cards](examples/cards.py) — cards, badges, progress, and theme switching.
- [Settings tabs](examples/tabs.py) — accessible tabs and panels.
- [Profile dialog](examples/dialog.py) — a native modal with an editable field.
- [FAQ accordion](examples/accordion.py) — expandable questions and answers.
- [Invoice table](examples/table.py) — a responsive table with status badges.
- [Preferences](examples/preferences.py) — a native select, slider, and switch.
- [Resource dropdown](examples/dropdown.py) — a dropdown menu with navigation links.
- [Dimensions popover](examples/popover.py) — editable fields inside a popover.
- [Toast notifications](examples/toast.py) — server-rendered notifications through HTMX.
- [Search input](examples/search.py) — an input group with a keyboard hint and query handling.
- [Empty state](examples/empty.py) — replace an empty state with a card through HTMX.

With the development dependencies installed, run an example from the project directory:

```sh
uv run --directory examples uvicorn form:app --reload
```

Replace `form` with any example's filename without `.py`, or copy an example into `main.py` and run `uv run uvicorn main:app --reload`.

### Components

Components accept children, `cls`, a `tag` override, and standard [FastHTML](https://github.com/AnswerDotAI/fasthtml) attributes. Variants and sizes have explicit `Literal` types for editor autocomplete and type checking; invalid values also raise `ValueError`.

```python
from fasthtml.common import H2, Header, Section
from fasthtml_basecoat import Card

Card(Header(H2("Account")), Section("Your account details"), size="sm")
```

Use native HTML elements for component children. See [Basecoat's component documentation](https://basecoatui.com/) for markup and behavior.

Tooltips work through attributes on any component:

```python
Button("Save", data_tooltip="Save your changes", data_side="bottom")
```

Chart is not supported yet. Chart.js integration is planned for a future release; Chart.js and Basecoat's chart helper are currently not bundled.

### Styles and JavaScript

`BasecoatInput()` returns the default Vega input. Supported styles are `vega`, `nova`, `maia`, `lyra`, `mira`, `luma`, `sera`, and `rhea`; `Style` and `STYLES` are also exported.

The input imports Tailwind and the bundled Basecoat source CSS. Tailwind detects utilities in your application automatically; the imported Basecoat bundle includes its component styles. For custom themes or additional source paths, use the standard `TailwindHead` arguments.

`BasecoatJS()` restores `localStorage.themeMode`, falling back to the system preference, then loads the bundled Basecoat JavaScript inline. Place it before `TailwindHead` to apply the theme before CSS loads. It accepts script attributes such as `nonce`; include it once for interactive components and `ThemeSwitcher`.

`Spinner` and `ThemeSwitcher` include their SVGs. For additional typed inline icons, see [fasthtml-lucide](https://github.com/SpaceShaman/fasthtml-lucide).

### Production

Use `TailwindHead(input=BasecoatInput("nova"))` with the default `watch=False`, then build CSS in your deployment pipeline:

```sh
uv run fasthtml-tailwindcss build main:app
```

For `app/main.py`, you can run `uv run fasthtml-tailwindcss build app.main:app` from the project directory. The build uses the application module's directory, so both approaches produce `app/static/tailwind.css` by default.

Deploy the generated stylesheet with the application. The compiler is only needed in the build environment.

## Development

### Setup and tests

```sh
uv sync --group dev
uv run --group dev python -m scripts.generate
uv run --group dev pytest
uv run --group dev ruff check src scripts tests hatch_build.py
```

The development group includes the generator dependencies and Tailwind compiler. They are not dependencies of the published wrapper. Theme bootstrap tests also use Node.js when available; the application does not require it.

### Regenerate components and assets

```sh
uv run --group dev python -m scripts.generate
```

This downloads the exact `basecoat-css` version from `pyproject.toml` (without a `.postN` suffix), verifies npm integrity, and downloads the matching GitHub tag. Source and npm versions must agree. The generator parses CSS once, produces ordinary Python functions, copies local assets, and updates `generation.json`. It stops if previously generated components disappear.

For local upstream sources:

```sh
uv run --group dev python -m scripts.generate --source ../basecoat --package /path/to/extracted/npm/package
```

Generated Python components and `generation.json` are committed to this repository. Composed helpers live in `helpers.py` and are not overwritten during regeneration. Input stylesheets register their Tailwind classes automatically. Downloaded CSS and JavaScript stay in the ignored `src/fasthtml_basecoat/assets/` directory. CI regenerates them before building packages.

### Build

```sh
uv build --no-sources
```

Generate assets first when building from a Git checkout; the build stops if they are missing. The universal wheel and source distribution include all CSS, JavaScript, and license notices, so installation and wheel builds from the source distribution need no Basecoat download. BeautifulSoup and tinycss2 are used only by the development generator.

### Automated releases

A daily [Release workflow](.github/workflows/release.yml) checks `basecoat-css` on npm. A new stable npm version triggers regeneration, wheel tests, and publication to PyPI. GitHub supplies only the matching source tag; it does not determine the released version.

Configure PyPI Trusted Publishing for repository `SpaceShaman/fasthtml-basecoatui`, workflow `release.yml`, and environment `pypi`. The workflow needs permission to commit generated files and version updates to the default branch.

### Manual releases

For Python-only fixes, run `uv version --bump post --no-sync`, commit and push the changes, then run **Actions → Release → Run workflow**. The workflow creates the tag and publishes the package. Versions follow Basecoat, with `.postN` for wrapper fixes.

## License

MIT. Bundled Basecoat resources retain their [upstream license](BASECOAT-LICENSE).

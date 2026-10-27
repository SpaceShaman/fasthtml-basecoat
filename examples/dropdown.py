from fasthtml.common import H1, A, Div, FastHTML, Main, P, StaticImmutable
from fasthtml_tailwindcss import TailwindHead

from fasthtml_basecoat import BasecoatInput, BasecoatJS, Button, DropdownMenu, Separator

app = FastHTML(
    hdrs=[BasecoatJS(), TailwindHead(input=BasecoatInput("nova"), watch=True)]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get():
    return Main(
        H1("Project resources", cls="text-2xl font-semibold"),
        P("Open the menu with a click or use the arrow keys."),
        DropdownMenu(
            Button(
                "Resources",
                id="resources-trigger",
                type="button",
                variant="outline",
                aria_haspopup="menu",
                aria_controls="resources-menu",
                aria_expanded="false",
            ),
            Div(
                Div(
                    A("Documentation", href="https://basecoatui.com/", role="menuitem"),
                    A(
                        "Source code",
                        href="https://github.com/SpaceShaman/fasthtml-basecoatui",
                        role="menuitem",
                    ),
                    Separator(),
                    A(
                        "Report an issue",
                        href="https://github.com/SpaceShaman/fasthtml-basecoatui/issues",
                        role="menuitem",
                    ),
                    id="resources-menu",
                    role="menu",
                    aria_labelledby="resources-trigger",
                ),
                data_popover=True,
                aria_hidden="true",
                cls="w-56",
            ),
            id="resources",
        ),
        cls="mx-auto max-w-xl space-y-6 p-6",
    )

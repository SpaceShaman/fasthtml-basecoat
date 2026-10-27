from fasthtml.common import (
    H1,
    H2,
    Div,
    FastHTML,
    Footer,
    Header,
    Main,
    P,
    Section,
    StaticImmutable,
)
from fasthtml_tailwindcss import TailwindHead

from fasthtml_basecoat import (
    Badge,
    BasecoatInput,
    BasecoatJS,
    Button,
    Card,
    CardAction,
    Progress,
    ThemeSwitcher,
)

app = FastHTML(
    hdrs=[BasecoatJS(), TailwindHead(input=BasecoatInput("nova"), watch=True)]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get():
    return Main(
        Header(
            H1("Your workspace", cls="text-2xl font-semibold"),
            ThemeSwitcher(),
            cls="flex items-center justify-between",
        ),
        Div(
            Card(
                Header(
                    H2("Getting started"),
                    P("Finish setting up your workspace."),
                    CardAction(Badge("In progress", variant="secondary")),
                ),
                Section(
                    Progress(value=60, max=100, aria_label="Setup progress"),
                    P(
                        "3 of 5 steps completed",
                        cls="mt-3 text-sm text-muted-foreground",
                    ),
                ),
                Footer(
                    Button("Continue setup", tag="a", href="https://basecoatui.com/")
                ),
            ),
            Card(
                Header(H2("Documentation"), P("Explore Basecoat components.")),
                Section(
                    P(
                        "Build interfaces with native HTML, utility classes, and a little JavaScript."
                    )
                ),
                Footer(
                    Button(
                        "Browse components",
                        tag="a",
                        href="https://basecoatui.com/",
                        variant="outline",
                    )
                ),
            ),
            cls="grid gap-6 md:grid-cols-2",
        ),
        cls="mx-auto max-w-4xl space-y-6 p-6",
    )

from fasthtml.common import H1, FastHTML, Form, Input, Main, P, Span, StaticImmutable
from fasthtml_tailwindcss import TailwindHead

from fasthtml_basecoat import BasecoatInput, BasecoatJS, Button, InputGroup, Kbd, Label

app = FastHTML(
    hdrs=[BasecoatJS(), TailwindHead(input=BasecoatInput("nova"), watch=True)]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get(q: str = ""):
    return Main(
        H1("Search the docs", cls="text-2xl font-semibold"),
        Form(
            Label("Search", fr="query"),
            InputGroup(
                Input(
                    id="query",
                    name="q",
                    value=q,
                    placeholder="Components, styles…",
                    type="search",
                ),
                Span(Kbd("Enter"), data_align="end", aria_hidden="true"),
            ),
            Button("Search", type="submit"),
            action="/",
            method="get",
            cls="grid gap-3",
        ),
        P(f"You searched for “{q}”." if q else "Enter a query to try the input group."),
        cls="mx-auto max-w-md space-y-6 p-6",
    )

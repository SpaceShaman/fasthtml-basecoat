from fasthtml.common import H2, Div, FastHTML, Header, Main, P, StaticImmutable
from fasthtml_tailwindcss import TailwindHead

from fasthtml_basecoat import (
    BasecoatInput,
    BasecoatJS,
    Button,
    Field,
    Input,
    Label,
    Popover,
)

app = FastHTML(
    hdrs=[BasecoatJS(), TailwindHead(input=BasecoatInput("nova"), watch=True)]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get():
    return Main(
        Popover(
            Button(
                "Dimensions",
                id="dimensions-trigger",
                type="button",
                variant="outline",
                aria_expanded="false",
                aria_controls="dimensions-content",
            ),
            Div(
                Header(H2("Dimensions"), P("Try editing the layer dimensions.")),
                Field(
                    Label("Width", fr="width"),
                    Input(id="width", value="100%", autofocus=True),
                ),
                Field(Label("Height", fr="height"), Input(id="height", value="300px")),
                id="dimensions-content",
                data_popover=True,
                aria_hidden="true",
                cls="w-72 space-y-4",
            ),
            id="dimensions",
        ),
        cls="min-h-dvh grid place-items-center p-6",
    )

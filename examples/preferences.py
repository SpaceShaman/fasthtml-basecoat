from fasthtml.common import (
    H2,
    FastHTML,
    Footer,
    Form,
    Header,
    Main,
    Option,
    P,
    Section,
    StaticImmutable,
)
from fasthtml_tailwindcss import TailwindHead

from fasthtml_basecoat import (
    BasecoatInput,
    BasecoatJS,
    Button,
    Card,
    Field,
    Label,
    NativeSelect,
    Slider,
    Switch,
)

app = FastHTML(
    hdrs=[BasecoatJS(), TailwindHead(input=BasecoatInput("nova"), watch=True)]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get():
    return Main(
        Card(
            Header(
                H2("Preferences"), P("Try native form controls styled with Basecoat.")
            ),
            Section(
                Form(
                    Field(
                        Label("Language", fr="language"),
                        NativeSelect(
                            Option("English", value="en"),
                            Option("Polish", value="pl"),
                            id="language",
                            name="language",
                        ),
                    ),
                    Field(
                        Label("Volume", fr="volume"),
                        Slider(
                            id="volume",
                            name="volume",
                            min=0,
                            max=100,
                            value=50,
                            cls="w-full",
                        ),
                    ),
                    Label(
                        Switch(name="notifications", checked=True),
                        "Email notifications",
                        cls="flex items-center gap-2",
                    ),
                    id="preferences",
                    method="get",
                    cls="grid gap-6",
                )
            ),
            Footer(
                Button("Reset", type="reset", form="preferences", variant="outline")
            ),
            cls="w-full max-w-md",
        ),
        cls="min-h-dvh grid place-items-center p-6",
    )

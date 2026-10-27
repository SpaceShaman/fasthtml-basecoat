from fasthtml.common import (
    H2,
    Div,
    FastHTML,
    Footer,
    Form,
    Header,
    Main,
    P,
    StaticImmutable,
)
from fasthtml_tailwindcss import TailwindHead

from fasthtml_basecoat import (
    BasecoatInput,
    BasecoatJS,
    Button,
    Dialog,
    Field,
    Input,
    Label,
)

app = FastHTML(
    hdrs=[BasecoatJS(), TailwindHead(input=BasecoatInput("nova"), watch=True)]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get():
    return Main(
        Button(
            "Edit display name",
            variant="outline",
            onclick="document.getElementById('profile').showModal()",
        ),
        Dialog(
            Div(
                Header(
                    H2("Edit profile", id="profile-title"),
                    P(
                        "Try editing your name. Close the preview when you're done.",
                        id="profile-description",
                    ),
                ),
                Form(
                    Field(
                        Label("Display name", fr="name"),
                        Input(id="name", value="Alex Morgan", autofocus=True),
                    ),
                    Footer(Button("Done", type="submit")),
                    method="dialog",
                    cls="grid gap-4",
                ),
                cls="sm:max-w-sm",
            ),
            id="profile",
            aria_labelledby="profile-title",
            aria_describedby="profile-description",
            onpointerdown="this.dataset.backdropPress = event.target === this",
            onclick="if (event.target === this && this.dataset.backdropPress === 'true') this.close()",
        ),
        cls="min-h-dvh grid place-items-center p-6",
    )

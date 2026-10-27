from fasthtml.common import (
    H2,
    FastHTML,
    Footer,
    Form,
    Header,
    Main,
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
    Input,
    Label,
    Textarea,
)

app = FastHTML(
    hdrs=[BasecoatJS(), TailwindHead(input=BasecoatInput("nova"), watch=True)]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get():
    return Main(
        Card(
            Header(H2("Contact us"), P("Send a message to our team.")),
            Section(
                Form(
                    Field(
                        Label("Name", fr="name"),
                        Input(id="name", name="name", required=True),
                    ),
                    Field(
                        Label("Email", fr="email"),
                        Input(id="email", name="email", type="email", required=True),
                    ),
                    Field(
                        Label("Message", fr="message"),
                        Textarea(id="message", name="message", required=True),
                    ),
                    id="contact",
                    action="/contact",
                    method="post",
                    cls="grid gap-4",
                )
            ),
            Footer(Button("Send message", type="submit", form="contact")),
            cls="w-full max-w-md",
        ),
        cls="min-h-dvh grid place-items-center p-6",
    )


@app.route("/contact", methods=["POST"])
def submit(name: str, email: str, message: str):
    return Main(
        Card(
            Header(H2("Message received"), P(f"Thanks, {name}!")),
            Section(P(message), P(f"We'll reply to {email}.")),
            Footer(Button("Back", tag="a", href="/", variant="outline")),
        ),
        cls="mx-auto max-w-md p-6",
    )

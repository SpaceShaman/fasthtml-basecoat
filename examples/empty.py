from fasthtml.common import H2, FastHTML, Footer, Header, Main, P, StaticImmutable
from fasthtml_tailwindcss import TailwindHead

from fasthtml_basecoat import BasecoatInput, BasecoatJS, Button, Card, Empty

app = FastHTML(
    hdrs=[BasecoatJS(), TailwindHead(input=BasecoatInput("nova"), watch=True)]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get():
    return Main(
        Empty(
            Header(
                H2("No projects yet"), P("Create your first project to get started.")
            ),
            Footer(
                Button("Create project", hx_post="/projects", hx_target="#projects")
            ),
            id="projects",
        ),
        cls="mx-auto max-w-xl p-6",
    )


@app.route("/projects", methods=["POST"])
def create():
    return Card(
        Header(H2("My first project"), P("Your project preview is ready.")),
        Footer(Button("Start over", tag="a", href="/", variant="outline")),
    )

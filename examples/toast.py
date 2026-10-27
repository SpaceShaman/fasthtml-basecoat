from fasthtml.common import H2, Div, FastHTML, Footer, Main, P, Section, StaticImmutable
from fasthtml_tailwindcss import TailwindHead

from fasthtml_basecoat import BasecoatInput, BasecoatJS, Button, Toast, ToastContent

app = FastHTML(
    hdrs=[BasecoatJS(), TailwindHead(input=BasecoatInput("nova"), watch=True)]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get():
    return Main(
        Button(
            "Show notification",
            variant="outline",
            hx_get="/notification",
            hx_target="#toaster",
            hx_swap="beforeend",
            hx_push_url="false",
        ),
        Div(id="toaster", cls="toaster"),
        cls="min-h-dvh grid place-items-center p-6",
    )


@app.route("/notification")
def notification():
    return Toast(
        ToastContent(
            Section(
                H2("All done!"), P("This notification was rendered on the server.")
            ),
            Footer(Button("Dismiss", type="button", data_toast_action=True)),
        ),
        role="status",
        aria_atomic="true",
        aria_hidden="false",
        data_category="success",
    )

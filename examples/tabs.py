from fasthtml.common import (
    H2,
    Div,
    FastHTML,
    Header,
    Main,
    Nav,
    P,
    Section,
    StaticImmutable,
)
from fasthtml.common import Button as TabButton
from fasthtml_tailwindcss import TailwindHead

from fasthtml_basecoat import (
    BasecoatInput,
    BasecoatJS,
    Card,
    Checkbox,
    Field,
    Input,
    Label,
    Tabs,
)

app = FastHTML(
    hdrs=[BasecoatJS(), TailwindHead(input=BasecoatInput("nova"), watch=True)]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get():
    return Main(
        Tabs(
            Nav(
                TabButton(
                    "Account",
                    type="button",
                    role="tab",
                    id="account-tab",
                    aria_controls="account-panel",
                    aria_selected="true",
                    tabindex="0",
                ),
                TabButton(
                    "Notifications",
                    type="button",
                    role="tab",
                    id="notifications-tab",
                    aria_controls="notifications-panel",
                    aria_selected="false",
                    tabindex="-1",
                ),
                role="tablist",
                aria_orientation="horizontal",
                aria_label="Settings",
            ),
            Div(
                Card(
                    Header(H2("Account"), P("Update your profile details.")),
                    Section(
                        Field(
                            Label("Display name", fr="name"),
                            Input(id="name", value="Alex Morgan"),
                        )
                    ),
                ),
                role="tabpanel",
                id="account-panel",
                aria_labelledby="account-tab",
                aria_selected="true",
                tabindex="-1",
            ),
            Div(
                Card(
                    Header(H2("Notifications"), P("Choose what you receive.")),
                    Section(
                        Label(
                            Checkbox(checked=True),
                            "Email notifications",
                            cls="flex items-center gap-2",
                        )
                    ),
                ),
                role="tabpanel",
                id="notifications-panel",
                aria_labelledby="notifications-tab",
                aria_selected="false",
                tabindex="-1",
                hidden=True,
            ),
            id="settings-tabs",
            cls="w-full max-w-md",
        ),
        cls="min-h-dvh grid place-items-center p-6",
    )

from fasthtml.common import (
    H1,
    Details,
    FastHTML,
    Main,
    Section,
    StaticImmutable,
    Summary,
)
from fasthtml.svg import Path, Svg
from fasthtml_tailwindcss import TailwindHead

from fasthtml_basecoat import Accordion, BasecoatInput, BasecoatJS

app = FastHTML(
    hdrs=[BasecoatJS(), TailwindHead(input=BasecoatInput("nova"), watch=True)]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get():
    questions = [
        (
            "What are your shipping options?",
            "Standard delivery takes 5–7 days. Express delivery takes 2–3 days.",
        ),
        (
            "Can I return my order?",
            "You can return unused items within 30 days of delivery.",
        ),
        (
            "How can I contact support?",
            "Email support@example.com and we'll be happy to help.",
        ),
    ]
    return Main(
        H1("Frequently asked questions", cls="text-2xl font-semibold"),
        Accordion(
            *(
                Details(
                    Summary(
                        question,
                        Svg(
                            Path(d="m6 9 6 6 6-6"),
                            viewBox="0 0 24 24",
                            width=24,
                            height=24,
                            fill="none",
                            stroke="currentColor",
                            stroke_width=2,
                            aria_hidden="true",
                        ),
                    ),
                    Section(answer),
                    open=index == 0,
                )
                for index, (question, answer) in enumerate(questions)
            )
        ),
        cls="mx-auto max-w-xl space-y-6 p-6",
    )

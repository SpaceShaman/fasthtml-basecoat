from fasthtml.common import (
    H1,
    Caption,
    FastHTML,
    Main,
    StaticImmutable,
    Tbody,
    Td,
    Th,
    Thead,
    Tr,
)
from fasthtml_tailwindcss import TailwindHead

from fasthtml_basecoat import Badge, BasecoatInput, BasecoatJS, Table, TableContainer

app = FastHTML(
    hdrs=[BasecoatJS(), TailwindHead(input=BasecoatInput("nova"), watch=True)]
)
app.mount("/static", StaticImmutable(directory="static"), name="static")


@app.route("/")
def get():
    invoices = [
        ("INV-001", "Paid", "$250.00"),
        ("INV-002", "Pending", "$150.00"),
        ("INV-003", "Paid", "$350.00"),
    ]
    return Main(
        H1("Invoices", cls="text-2xl font-semibold"),
        TableContainer(
            Table(
                Caption("Your recent invoices."),
                Thead(
                    Tr(
                        Th("Invoice", scope="col"),
                        Th("Status", scope="col"),
                        Th("Amount", scope="col", cls="text-right"),
                    )
                ),
                Tbody(
                    *(
                        Tr(
                            Th(number, scope="row"),
                            Td(
                                Badge(
                                    status,
                                    variant="secondary"
                                    if status == "Paid"
                                    else "outline",
                                )
                            ),
                            Td(amount, cls="text-right"),
                        )
                        for number, status, amount in invoices
                    )
                ),
            )
        ),
        cls="mx-auto max-w-3xl space-y-6 p-6",
    )

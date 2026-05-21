from app.invoice.utils.pdf_utils import render_html_to_pdf


customer_name = "John Doe"
items = [
    {
        "name": "Book",
        "quantity": 5,
        "price": 100
    }
]

render_html_to_pdf(customer_name, items)
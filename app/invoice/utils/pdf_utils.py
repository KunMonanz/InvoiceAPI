import os
import re
import uuid

from jinja2 import Environment, FileSystemLoader

from app.config.settings import settings
from app.invoice.dto import FilenamePathDTO
from app.invoice.error import MissingTemplateException

os.getenv("WEASYPRINT_DLL_DIRECTORIES")

from weasyprint import HTML


def render_html_to_pdf(
    customer_name: str, items: list[dict], business_name: str | None = None
):
    """To generate pdf from user input

    Args:
        - customer_name: The name of the customer the invoice is to
        - item: A list that contains a dictionary with keys
                - name: The name of the item
                - quantity: The amount of the item
                - price: The price of one unit of the item
    Return:
        A pdf in byte form

    """

    try:
        env = Environment(loader=FileSystemLoader("."))

        template = env.get_template("app/templates/invoice.html")

        if not template:
            raise MissingTemplateException

        grand_total = 0
        processed_items = []
        for item in items:
            qty = int(item.get("quantity", 0))
            price = float(item.get("price", 0))
            item_total = qty * price
            grand_total += item_total

            processed_items.append(
                {
                    "name": item.get("name"),
                    "quantity": qty,
                    "price": f"{price:.2f}",
                    "total": f"{item_total:.2f}",
                }
            )

        html = template.render(
            business_name=business_name,
            customer_name=customer_name,
            items=processed_items,
            grand_total=f"{grand_total:.2f}",
        )

        return HTML(string=html).write_pdf()
    except Exception:
        raise


def generate_pdf_file_name(customer_name: str) -> FilenamePathDTO:
    """Generates a unique PDF file name based on the customer name and a UUID.

    Args:
        customer_name: The name of the customer for whom the invoice is generated.
    """
    safe_name = re.sub(r"[^\w\-]", "_", customer_name.strip())
    unique_id = uuid.uuid4().hex[:8]
    filename = f"invoice_{safe_name}_{unique_id}.pdf"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    return FilenamePathDTO(filename=filename, file_path=file_path)

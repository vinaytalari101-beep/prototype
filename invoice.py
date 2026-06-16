from fpdf import FPDF, XPos, YPos
import uuid
import os


def generate_invoice(
        customer,
        items,
        grand_total):

    invoice_no = str(
        uuid.uuid4()
    )[:8]

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Helvetica",
        "B",
        16
    )

    pdf.cell(
        200,
        10,
        "SMART INVENTORY STORE",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        align="C"
    )

    pdf.ln(10)

    pdf.set_font(
        "Helvetica",
        "",
        12
    )

    pdf.cell(
        200,
        10,
        f"Invoice No: {invoice_no}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT
    )

    pdf.cell(
        200,
        10,
        f"Customer: {customer}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT
    )

    pdf.ln(5)

    pdf.cell(
        70,
        10,
        "Product",
        border=1
    )

    pdf.cell(
        40,
        10,
        "Qty",
        border=1
    )

    pdf.cell(
        40,
        10,
        "Price",
        border=1
    )

    pdf.cell(
        40,
        10,
        "Total",
        border=1,
        ln=True
    )

    for item in items:

        pdf.cell(
            70,
            10,
            item["name"],
            border=1
        )

        pdf.cell(
            40,
            10,
            str(item["qty"]),
            border=1
        )

        pdf.cell(
            40,
            10,
            str(item["price"]),
            border=1
        )

        pdf.cell(
            40,
            10,
            str(item["total"]),
            border=1,
            ln=True
        )

    pdf.ln(10)

    pdf.set_font(
        "Arial",
        "B",
        14
    )

    pdf.cell(
        200,
        10,
        f"Grand Total: Rs. {grand_total}",
        ln=True
    )

    os.makedirs(
        "invoices",
        exist_ok=True
    )

    file_path = f"invoices/{invoice_no}.pdf"

    pdf.output(file_path)

    return file_path, invoice_no
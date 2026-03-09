# sales_app/utils/pdf_generator.py
try:
    from reportlab.lib.pagesizes import A5
    from reportlab.pdfgen import canvas
except ImportError:
    raise ImportError("reportlab is not installed. Install it using: pip install reportlab")
from pathlib import Path

def generate_receipt_pdf(sale, output_dir=None):
    if output_dir is None:
        output_dir = Path(__file__).resolve().parents[2] / "reports" / "generated_pdfs"
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / f"receipt_{sale.id}.pdf"
    c = canvas.Canvas(str(filepath), pagesize=A5)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, 400, "SHOP NAME")
    c.setFont("Helvetica", 10)
    c.drawString(40, 380, f"Sale ID: {sale.id}")
    c.drawString(40, 365, f"Date: {sale.date.strftime('%Y-%m-%d %H:%M')}")
    y = 340
    c.drawString(40, y, "Item")
    c.drawString(200, y, "Qty")
    c.drawString(260, y, "Price")
    y -= 15
    for item in sale.items.all():
        c.drawString(40, y, item.product.name)
        c.drawString(200, y, str(item.quantity))
        c.drawString(260, y, str(item.price))
        y -= 15
    c.drawString(40, y-10, f"Total: {sale.total_amount}")
    c.save()
    return filepath
# Note: This is a basic implementation. You can enhance the PDF layout and styling as needed.
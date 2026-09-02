from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from sqlmodel import Session, select
from io import BytesIO

from ..models import Order, OrderItem, Customer
from ..core.database import get_session

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

RESTAURANT_INFO = {
    "name": "Mon Restaurant",
    "address": "123 Rue Principale, Antananarivo 101, Madagascar",
    "phone": "+261 34 00 000 00",
    "email": "contact@monrestaurant.mg",
}


def generate_invoice_pdf(order: Order, items: list, customer: Customer | None) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=4,
        alignment=1,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=16,
        spaceAfter=8,
    )

    elements = []

    elements.append(Paragraph(RESTAURANT_INFO["name"], title_style))
    elements.append(Paragraph(RESTAURANT_INFO["address"], subtitle_style))
    elements.append(Paragraph(RESTAURANT_INFO["phone"], subtitle_style))
    elements.append(Paragraph(RESTAURANT_INFO["email"], subtitle_style))
    elements.append(Spacer(1, 8 * mm))

    elements.append(Paragraph(
        "FACTURE",
        ParagraphStyle("InvoiceTitle", parent=styles["Heading1"], fontSize=18,
                        textColor=colors.HexColor("#1e293b"), alignment=1, spaceAfter=4),
    ))
    elements.append(Paragraph(
        f"N\u00b0 {order.orderNumber}",
        ParagraphStyle("InvoiceNumber", parent=styles["Normal"], fontSize=12,
                        textColor=colors.HexColor("#64748b"), alignment=1, spaceAfter=16),
    ))

    date_str = order.createdAt.strftime("%d/%m/%Y") if order.createdAt else ""
    payment_status = {
        "UNPAID": "En attente",
        "PAID": "Pay\u00e9",
        "CANCELLED": "Annul\u00e9",
        "REFUNDED": "Rembours\u00e9",
    }.get(str(order.paymentStatus), str(order.paymentStatus))

    info_data = [
        ["Date", date_str],
        ["Statut paiement", payment_status],
        ["Client", f"{customer.firstName} {customer.lastName}" if customer else "Client invit\u00e9"],
    ]
    if customer and customer.phone:
        info_data.append(["T\u00e9l\u00e9phone", customer.phone])
    if customer and customer.email:
        info_data.append(["Email", customer.email])

    info_table = Table(info_data, colWidths=[45 * mm, 120 * mm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#64748b")),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#1e293b")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8 * mm))

    elements.append(Paragraph("D\u00e9tails de la commande", heading_style))

    def fmt_ar(v: float) -> str:
        return f"{v:,.0f} Ar".replace(",", " ")

    item_data = [["Produit", "Qt\u00e9", "Prix unitaire", "Total"]]
    for item in items:
        item_total = round(item.totalPrice or (item.price * item.quantity), 2)
        name = "Produit supprim\u00e9"
        try:
            if hasattr(item, "menuItem") and item.menuItem:
                name = item.menuItem.name
        except Exception:
            pass
        unit_price = round(item_total / item.quantity, 2) if item.quantity else 0
        item_data.append([
            name,
            str(item.quantity),
            fmt_ar(unit_price),
            fmt_ar(item_total),
        ])

    items_table = Table(item_data, colWidths=[85 * mm, 15 * mm, 35 * mm, 35 * mm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 6 * mm))

    subtotal = sum(round(it.totalPrice or 0, 2) for it in items)
    tax = round(subtotal * 0.2, 2)
    total = round(order.totalAmount or subtotal + tax, 2)

    totals_data = [
        ["Sous-total", fmt_ar(subtotal)],
        ["TVA (20%)", fmt_ar(tax)],
        ["TOTAL", fmt_ar(total)],
    ]
    totals_table = Table(totals_data, colWidths=[135 * mm, 35 * mm])
    totals_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 12),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.HexColor("#1e293b")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEABOVE", (0, -1), (-1, -1), 2, colors.HexColor("#1e293b")),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 12 * mm))

    elements.append(Paragraph(
        "Merci de votre visite !",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=10,
                        textColor=colors.HexColor("#94a3b8"), alignment=1),
    ))
    elements.append(Paragraph(
        "Cette facture est g\u00e9n\u00e9r\u00e9e automatiquement.",
        ParagraphStyle("Footer2", parent=styles["Normal"], fontSize=8,
                        textColor=colors.HexColor("#94a3b8"), alignment=1),
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


@router.get("/{order_id}")
def download_invoice(
    order_id: str,
    session: Session = Depends(get_session),
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    items = session.exec(select(OrderItem).where(OrderItem.orderId == order_id)).all()
    customer = session.get(Customer, order.customerId) if order.customerId else None

    pdf_buffer = generate_invoice_pdf(order, items, customer)

    filename = f"facture-{order.orderNumber}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

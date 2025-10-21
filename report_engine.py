from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.platypus import HRFlowable, Image, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from io import BytesIO
from streamlit import session_state as ss

from data_viz import plot_irl

BG_COLOR = HexColor("#333C4E")

def measure(text, font='Helvetica-Bold', size=10, padding=6):

    return stringWidth(text, font, size) + padding

def get_irl_table(irl_ass):
    irl_headers = ["IRL", "Level", "Notes"]
    irl_col_widths = [measure(irl_headers[0], padding=20),
                      measure(irl_headers[1], padding=20),
                      None]
    irl_data = [
        irl_headers,
        ["CRL", f"{irl_ass.crl}", Paragraph(irl_ass.crl_notes or "")],
        ["TRL", f"{irl_ass.trl}", Paragraph(irl_ass.trl_notes or "")],
        ["BRL", f"{irl_ass.brl}", Paragraph(irl_ass.brl_notes or "")],
        ["IPRL", f"{irl_ass.iprl}", Paragraph(irl_ass.iprl_notes or "")],
        ["TMRL", f"{irl_ass.tmrl}", Paragraph(irl_ass.tmrl_notes or "")],
        ["FRL", f"{irl_ass.frl}", Paragraph(irl_ass.frl_notes or "")]
    ]

    irl_table = Table(irl_data,
                      hAlign='LEFT',
                      vAlign='TOP',
                      colWidths=irl_col_widths)
    irl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN',(0, 0), (-1, -1), 'TOP' ),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ]))

    return irl_table


def get_project_report(irl_ass):

    col_w = (A4[0]-40)/2
    # Create PDF buffer in memory.
    pdf_buffer = BytesIO()

    # Create the PDF document
    doc = SimpleDocTemplate(pdf_buffer,
                            pagesize=A4,
                            leftMargin=20,
                            rightMargin=20,
                            topMargin=20,
                            bottomMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    # Add a title
    title = Paragraph(f"Project Summary Report<br/>{irl_ass.project_name}", styles['Title'])
    elements.append(title)
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))  # Horizontal line

    # Add header.
    header_data = [[Paragraph(f"<b>Really Nice IRL Project Number:</b> {irl_ass.project_no}",
                             styles['BodyText']),
                    Paragraph(f"<b>Assessment Date:</b> {irl_ass.assessment_date}",
                             styles['BodyText'])]
                   ]
    header_table = Table(header_data, colWidths=[col_w, col_w])
    header_table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                            ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
                        ]))
    elements.append(Spacer(1, 12))
    elements.append(header_table)
    elements.append(Paragraph(f"<b>Project Description:</b> {irl_ass.project_description}",
                    styles['BodyText']))
    elements.append(Spacer(1, 12))

    # Fetch the plot
    spider = plot_irl(irl_ass,
                      smooth=ss.user_settings.smooth_irl,
                      dark_mode=False,
                      targets=False)
    spider_buf = BytesIO()
    spider.savefig(spider_buf, format="png", bbox_inches="tight", dpi=300)
    spider_buf.seek(0)
    pil_img = PILImage.open(spider_buf)
    img_w_px, img_h_px = pil_img.size
    aspect = img_h_px / img_w_px
    # Desired width in points (e.g., 300)
    d_width = 250
    d_height = d_width * aspect
    spider_buf.seek(0)
    spider_img = Image(spider_buf, width=d_width, height=d_height)

    # Add IRL table
    irl_table = get_irl_table(irl_ass)

    # Prepare right hand side (notes)
    notes_para = Paragraph(irl_ass.project_notes or "", styles['BodyText'])
    notes_spacer = Spacer(1, 12)
    notes_head = Paragraph("<b>Project notes:</b>", styles['BodyText'])
    r_col = [notes_spacer, notes_head, notes_para]

    # Create a borderless two-column table
    top_table = Table(
        [[spider_img, r_col]],
        colWidths=[col_w, col_w]  # Adjust widths as needed
    )
    top_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0, colors.white),  # No border
        ('INNERGRID', (0, 0), (-1, -1), 0, colors.white),  # No grid
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))  # Horizontal line
    elements.append(top_table)
    elements.append(irl_table)

    # Build the PDF
    doc.build(elements)
    pdf_buffer.seek(0)

    return pdf_buffer

def get_portfolio_report(portfolio):
    col_w = (A4[0]-40)/2
    # Create PDF buffer in memory.
    pdf_buffer = BytesIO()

    # Create the PDF document
    doc = SimpleDocTemplate(pdf_buffer,
                            pagesize=A4,
                            leftMargin=20,
                            rightMargin=20,
                            topMargin=20,
                            bottomMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    for irl_ass in portfolio:

        title = Paragraph(f"{irl_ass.project_name}", styles['Title'])
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))  # Horizontal line
        elements.append(Spacer(1, 12))
        elements.append(title)
        # Add header.
        header_data = [[Paragraph(f"<b>Really Nice IRL Project Number:</b> {irl_ass.project_no}",
                                styles['BodyText']),
                        Paragraph(f"<b>Assessment Date:</b> {irl_ass.assessment_date}",
                                styles['BodyText'])]
                    ]
        header_table = Table(header_data, colWidths=[col_w, col_w])
        header_table.setStyle(TableStyle([
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 0), (-1, -1), 10),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                                ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
                            ]))
        elements.append(header_table)
        elements.append(Paragraph(f"<b>Project Description:</b> {irl_ass.project_description}",
                        styles['BodyText']))
        elements.append(Spacer(1, 12))        
        irl_table = get_irl_table(irl_ass)
        elements.append(irl_table)
        notes_spacer = Spacer(1, 12)
        notes_head = Paragraph("<b>Project notes:</b>", styles['BodyText'])
        notes_para = Paragraph(irl_ass.project_notes or "", styles['BodyText'])
        elements.append(notes_spacer)
        elements.append(notes_head)
        elements.append(notes_para)

    # Build the PDF
    doc.build(elements)
    pdf_buffer.seek(0)

    return pdf_buffer

# Maps report names to functions and whether they need a project or portfolio.
AVAILABLE_REPORTS = {
    "Project Assessment Report" : [get_project_report, False],
    "Portfolio Report": [get_portfolio_report, True]
}
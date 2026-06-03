import os
from reportlab.lib.pagesizes    import A4
from reportlab.lib.styles       import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units        import inch, cm
from reportlab.lib               import colors
from reportlab.platypus         import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable
)
from reportlab.pdfbase          import pdfmetrics
from reportlab.pdfbase.ttfonts  import TTFont


def _register_fonts():
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    dev_path = os.path.join(font_dir, "NotoSansDevanagari-Regular.ttf")
    if os.path.exists(dev_path):
        try:
            pdfmetrics.registerFont(TTFont("NotoDevanagari", dev_path))
        except Exception:
            pass


def _build_styles(language: str) -> dict:
    base  = getSampleStyleSheet()
    hindi = language in ("Hindi", "Marathi")
    font  = "NotoDevanagari" if hindi else "Helvetica"

    return {
        "title": ParagraphStyle(
            "Title", parent=base["Normal"],
            fontName=font + "-Bold" if not hindi else font,
            fontSize=13, alignment=1,
            spaceAfter=6, textColor=colors.HexColor("#1a1a1a")
        ),
        "subtitle": ParagraphStyle(
            "Sub", parent=base["Normal"],
            fontName=font, fontSize=11,
            alignment=1, spaceAfter=4,
            textColor=colors.HexColor("#444444")
        ),
        "label": ParagraphStyle(
            "Label", parent=base["Normal"],
            fontName=font, fontSize=10,
            textColor=colors.HexColor("#666666"), spaceAfter=2
        ),
        "body": ParagraphStyle(
            "Body", parent=base["Normal"],
            fontName=font, fontSize=10.5,
            leading=16, spaceAfter=8,
            textColor=colors.HexColor("#1a1a1a")
        ),
        "flag": ParagraphStyle(
            "Flag", parent=base["Normal"],
            fontName=font, fontSize=10,
            textColor=colors.HexColor("#993C1D"),
            backColor=colors.HexColor("#FAECE7"),
            spaceAfter=6, leftIndent=8, rightIndent=8,
            borderPadding=(4, 6, 4, 6)
        ),
        "disclaimer": ParagraphStyle(
            "Disc", parent=base["Normal"],
            fontName=font, fontSize=9,
            textColor=colors.HexColor("#633806"),
            backColor=colors.HexColor("#FAEEDA"),
            leading=14, spaceAfter=6,
            borderPadding=(6, 8, 6, 8)
        ),
        "small": ParagraphStyle(
            "Small", parent=base["Normal"],
            fontName=font, fontSize=9,
            textColor=colors.HexColor("#888888"), spaceAfter=2
        ),
    }


def generate_bail_pdf(
    application_text: str,
    fir_data:         dict,
    bail_eligibility: dict,
    confidence_score: float,
    flagged_sections: list,
    output_path:      str,
    language:         str = "English"
) -> str:

    _register_fonts()
    styles = _build_styles(language)

    doc = SimpleDocTemplate(
        output_path,
        pagesize    = A4,
        rightMargin = 2.2 * cm,
        leftMargin  = 2.2 * cm,
        topMargin   = 2.0 * cm,
        bottomMargin= 2.0 * cm
    )

    story = []

    # ── Header ─────────────────────────────────────────────────────
    story.append(Paragraph("IN THE COURT OF THE HONOURABLE JUDICIAL MAGISTRATE", styles["title"]))
    district = fir_data.get("district", "___________")
    state_nm = fir_data.get("state",    "___________")
    story.append(Paragraph(f"{district}, {state_nm}", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#185FA5"), spaceAfter=10))

    # ── Case details table ─────────────────────────────────────────
    table_data = [
        ["FIR Number",     fir_data.get("fir_number",     "___________")],
        ["Police Station", fir_data.get("police_station", "___________")],
        ["Accused",        fir_data.get("accused_name",   "The Applicant")],
        ["Sections",       ", ".join(fir_data.get("sections_charged", []))],
        ["Date of FIR",    fir_data.get("date_of_fir",    "___________")],
    ]

    table = Table(table_data, colWidths=[4.5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("FONTSIZE",    (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR",   (0, 0), (0, -1),  colors.HexColor("#666666")),
        ("TEXTCOLOR",   (1, 0), (1, -1),  colors.HexColor("#1a1a1a")),
        ("FONTNAME",    (0, 0), (0, -1),  "Helvetica-Bold"),
        ("TOPPADDING",  (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1),  3),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),
            [colors.HexColor("#F8F8F8"), colors.white]),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * inch))

    # ── Bail eligibility banner ────────────────────────────────────
    eligible     = bail_eligibility.get("eligible", False)
    bail_section = bail_eligibility.get("section",  "BNSS Section 479")
    reason       = bail_eligibility.get("reason",   "")

    banner_color = "#E1F5EE" if eligible else "#E6F1FB"
    text_color   = "#085041" if eligible else "#0C447C"
    label        = "BAIL AS A RIGHT" if eligible else "STANDARD BAIL APPLICATION"

    banner_style = ParagraphStyle(
        "Banner", fontSize=10, fontName="Helvetica-Bold",
        backColor=colors.HexColor(banner_color),
        textColor=colors.HexColor(text_color),
        borderPadding=(6, 8, 6, 8), spaceAfter=4
    )
    story.append(Paragraph(f"⚖ {label} — {bail_section}", banner_style))

    reason_style = ParagraphStyle(
        "Reason", fontSize=9, fontName="Helvetica",
        backColor=colors.HexColor(banner_color),
        textColor=colors.HexColor(text_color),
        borderPadding=(2, 8, 6, 8), spaceAfter=12
    )
    story.append(Paragraph(reason, reason_style))

    # ── Confidence bar ─────────────────────────────────────────────
    pct  = int(confidence_score * 100)
    conf_color = "#085041" if pct >= 80 else "#633806" if pct >= 60 else "#993C1D"
    story.append(Paragraph(
        f"AI Confidence Score: {pct}%  "
        f"{'(High — suitable for filing after lawyer review)' if pct>=80 else '(Review flagged sections before filing)'}",
        ParagraphStyle("Conf", fontSize=9, fontName="Helvetica",
                       textColor=colors.HexColor(conf_color), spaceAfter=8)
    ))

    story.append(HRFlowable(width="100%", thickness=0.5,
                            color=colors.HexColor("#dddddd"), spaceAfter=10))

    # ── Main application text ──────────────────────────────────────
    for para in application_text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        if para.isupper() or para.startswith("IN THE") or para.startswith("TO"):
            story.append(Paragraph(para, styles["title"]))
        elif "[VERIFY" in para or "[FLAGGED" in para:
            story.append(Paragraph(para, styles["flag"]))
        else:
            story.append(Paragraph(para, styles["body"]))

    story.append(Spacer(1, 0.2 * inch))

    # ── Flagged sections summary ────────────────────────────────────
    if flagged_sections:
        story.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor("#dddddd"), spaceAfter=8))
        story.append(Paragraph(
            f"⚠ {len(flagged_sections)} section(s) flagged for lawyer review:",
            styles["flag"]
        ))
        for flag in flagged_sections:
            story.append(Paragraph(f"• {flag}", styles["flag"]))
        story.append(Spacer(1, 0.1 * inch))

    # ── Disclaimer ─────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#FAEEDA"), spaceAfter=6))
    story.append(Paragraph(
        "IMPORTANT DISCLAIMER: This document is an AI-generated draft produced by Nyaya Saathi. "
        "It must be reviewed and verified by a qualified advocate before filing. "
        "This is not legal advice. Citations marked [VERIFY] must be manually confirmed. "
        "Nyaya Saathi is a legal literacy tool — not a substitute for professional legal counsel.",
        styles["disclaimer"]
    ))

    # ── Footer ─────────────────────────────────────────────────────
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(
        "Generated by Nyaya Saathi — AI Legal Accessibility Platform | nyayasaathi.in",
        styles["small"]
    ))

    doc.build(story)
    return output_path
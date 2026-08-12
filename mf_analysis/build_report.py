"""Generate the final Bluestock MF PDF report."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
import os

OUT = "Final_Report.pdf"

SECTION_TEXT = {
    "executive_summary": (
        "This report summarizes the Bluestock MF capstone project. "
        "It explains the investment problem, data sources, ETL design, exploratory data analysis, performance analytics, dashboard insights, limitations, and recommendations. "
        "The report is intended for stakeholders seeking a data-driven mutual fund selection framework for Indian equity schemes."
    ),
    "data_sources": (
        "Data sources include synthetic master datasets and live NAV feeds. "
        "The project combines AMFI scheme metadata, NAV history, portfolio holdings, SIP records, returns, AUM, benchmark data, expense ratios, fund manager details, and risk metrics. "
        "Live NAV values are fetched from MFAPI to supplement historical model outputs."
    ),
    "etl_design": (
        "The ETL design follows a structured pipeline: generate base datasets, clean raw inputs, load structured tables, and produce analytics-ready outputs. "
        "Raw CSVs are transformed into normalized tables and verified for schema consistency, data quality, and AMFI scheme coverage. "
        "The pipeline supports repeatable execution and report regeneration with a single orchestration script."
    ),
    "eda_findings": (
        "Exploratory Data Analysis highlights NAV distribution, volatility trends, correlation structure, and expense ratio patterns. "
        "Key findings show how liquidity, expense ratios, and sector allocation drive performance differences across large-cap schemes. "
        "Return profiles reveal that low volatility schemes tend to underperform on multi-year CAGR but provide improved risk-adjusted outcomes."
    ),
    "performance_analysis": (
        "Performance analysis examines CAGR, Sharpe ratio, Sortino ratio, alpha/beta, drawdowns, and fund scorecard metrics. "
        "The analysis identifies top-performing schemes across 1-year, 3-year, and 5-year horizons and quantifies downside risk through VaR/CVaR. "
        "Sector concentration and SIP continuity metrics also inform suitability for conservative and growth-focused investors."
    ),
    "dashboard_screenshots": (
        "The dashboard visualizes key insights, including follow-on charts for NAV trends, fund comparison, portfolio composition, and investor analytics. "
        "Screenshots capture the reporting experience and surface actionable findings for portfolio managers and retail investors."
    ),
    "limitations": (
        "The analysis uses synthetic NAV history for model testing and a limited set of 20 sample schemes. "
        "Live NAV values are sampled from MFAPI and may not represent all plan variants or direct/regular distinctions. "
        "Future work should expand the universe, incorporate actual AMFI daily feeds, and validate with client-level SIP behavior."
    ),
    "recommendations": (
        "Recommendations include focusing on funds with strong risk-adjusted returns, controlling expense ratio leakage, and monitoring sector concentration. "
        "The dashboard can be used to track fund rankings, SIP continuity, and portfolio risk metrics over time. "
        "The capstone project should evolve into an automated reporting service with scheduled data updates and an investor-facing dashboard."
    ),
}


def add_paragraphs(story, title, text, styles):
    story.append(Paragraph(title, styles["Heading2"]))
    story.append(Spacer(1, 12))
    for paragraph in text.split("\n\n"):
        story.append(Paragraph(paragraph, styles["BodyText"]))
        story.append(Spacer(1, 12))


def find_images():
    images = []
    for root, _, files in os.walk("dashboard"):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                images.append(os.path.join(root, file))
    return sorted(images)[:6]


def build():
    doc = SimpleDocTemplate(OUT, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    styles["BodyText"].alignment = TA_JUSTIFY
    styles.add(ParagraphStyle(name="Centered", parent=styles["Heading1"], alignment=TA_CENTER))

    story = []
    story.append(Paragraph("Bluestock MF Capstone Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("A final project report covering data sources, ETL design, EDA, performance analysis, and dashboard insights.", styles["BodyText"]))
    story.append(PageBreak())

    add_paragraphs(story, "Executive Summary", SECTION_TEXT["executive_summary"], styles)
    story.append(PageBreak())
    add_paragraphs(story, "Data Sources", SECTION_TEXT["data_sources"], styles)
    story.append(PageBreak())
    add_paragraphs(story, "ETL Design", SECTION_TEXT["etl_design"], styles)
    story.append(PageBreak())
    add_paragraphs(story, "Exploratory Data Analysis Findings", SECTION_TEXT["eda_findings"], styles)
    story.append(PageBreak())
    add_paragraphs(story, "Performance Analysis", SECTION_TEXT["performance_analysis"], styles)
    story.append(PageBreak())
    add_paragraphs(story, "Dashboard Screenshots", SECTION_TEXT["dashboard_screenshots"], styles)

    images = find_images()
    for image_path in images:
        try:
            story.append(Image(image_path, width=450, height=250))
            story.append(Spacer(1, 12))
        except Exception:
            continue
    story.append(PageBreak())

    add_paragraphs(story, "Limitations", SECTION_TEXT["limitations"], styles)
    story.append(PageBreak())
    add_paragraphs(story, "Recommendations", SECTION_TEXT["recommendations"], styles)
    story.append(Spacer(1, 12))
    story.append(Paragraph("Final deliverables generated by build_report.py.", styles["BodyText"]))
    doc.build(story)
    print(f"Generated report: {OUT}")


if __name__ == "__main__":
    build()

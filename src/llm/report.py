import sqlite3
import pandas as pd
from src.llm.client import call_llm
from src.llm.prompts import REPORT_INSTRUCTION
from src.utils.config import DB_PATH
from src.llm.summarise import get_product_name

# for pdf export
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
from pathlib import Path
import re

def generate_report(parent_asin):
    """
    Generate a full executive report for a product.
    Uses instruction-based prompting with structured data injection.
    """
    conn = sqlite3.connect(DB_PATH)
    
    # product stats
    stats = pd.read_sql("""
        SELECT 
            COUNT(*) as review_count,
            ROUND(AVG(rating), 2) as avg_rating,
            ROUND(AVG(CASE WHEN sentiment=1 THEN 100.0 ELSE 0 END), 1) as positive_pct,
            ROUND(AVG(CASE WHEN sentiment=0 THEN 100.0 ELSE 0 END), 1) as negative_pct
        FROM reviews_clean
        WHERE parent_asin = ?
    """, conn, params=(parent_asin,))
    
    # aspect summary
    aspects = pd.read_sql("""
        SELECT aspect, sentiment, COUNT(*) as count
        FROM aspects
        WHERE parent_asin = ?
        GROUP BY aspect, sentiment
        ORDER BY count DESC
        LIMIT 10
    """, conn, params=(parent_asin,))
    
    # sample reviews (mix of positive and negative)
    samples = pd.read_sql("""
        SELECT text, rating FROM reviews_clean
        WHERE parent_asin = ?
        ORDER BY helpful_vote DESC
        LIMIT 6
    """, conn, params=(parent_asin,))
    
    conn.close()
    
    product_name = get_product_name(parent_asin)
    
    aspects_summary = aspects.to_string(index=False) if len(aspects) > 0 else "No aspect data available"
    sample_reviews = "\n".join([
        f"- ({row['rating']}★) {row['text'][:150]}"
        for _, row in samples.iterrows()
    ])
    
    prompt = REPORT_INSTRUCTION.format(
        product_name=product_name,
        review_count=int(stats["review_count"].iloc[0]),
        avg_rating=float(stats["avg_rating"].iloc[0]),
        positive_pct=float(stats["positive_pct"].iloc[0]),
        negative_pct=float(stats["negative_pct"].iloc[0]),
        aspects_summary=aspects_summary,
        sample_reviews=sample_reviews
    )
    
    report = call_llm(prompt, max_tokens=2000)
    
    return {
        "parent_asin": parent_asin,
        "product_name": product_name,
        "stats": stats.to_dict(orient="records")[0],
        "report": report
    }
    

def save_report_pdf(report_data, output_path="reports/executive_report.pdf"):
    """
    Convert the LLM-generated executive report text into a PDF file.
    """
    Path("reports").mkdir(exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )
    
    styles = getSampleStyleSheet()
    
    # custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceAfter=6,
        spaceBefore=12
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=6,
        leading=14
    )
    meta_style = ParagraphStyle(
        "MetaStyle",
        parent=styles["Normal"],
        fontSize=9,
        spaceAfter=4,
        textColor="grey"
    )
    
    story = []
    
    # title
    story.append(Paragraph("Executive Report", title_style))
    story.append(Paragraph(
        f"Product: {report_data['product_name']}", heading_style
    ))
    
    # stats summary box
    stats = report_data["stats"]
    story.append(Paragraph(
        f"Reviews Analyzed: {stats['review_count']} | "
        f"Avg Rating: {stats['avg_rating']} | "
        f"Positive: {stats['positive_pct']}% | "
        f"Negative: {stats['negative_pct']}%",
        meta_style
    ))
    story.append(Spacer(1, 0.2 * inch))
    
    # parse and render report body
    # split by markdown headers (##) and bold (**text**)
    report_text = report_data["report"]
    lines = report_text.split("\n")
    
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.1 * inch))
            continue
        
        # markdown heading → PDF heading
        if line.startswith("## ") or line.startswith("### "):
            text = line.lstrip("#").strip()
            story.append(Paragraph(text, heading_style))
        
        # bold text (**text**) → clean and render
        elif line.startswith("**") and line.endswith("**"):
            text = line.strip("*")
            story.append(Paragraph(f"<b>{text}</b>", body_style))
        
        # bullet points
        elif line.startswith("*   ") or line.startswith("-   "):
            text = line.lstrip("*- ").strip()
            # clean remaining markdown bold
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            story.append(Paragraph(f"• {text}", body_style))
        
        # regular paragraph
        else:
            # clean markdown bold inline
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            story.append(Paragraph(text, body_style))
    
    doc.build(story)
    print(f"PDF saved → {output_path}")
    return output_path

if __name__ == "__main__":
    result = generate_report("B075X8471B")
    print(f"Executive Report: {result['product_name']}")
    print(f"Stats: {result['stats']}")
    print(f"\n{result['report']}")
    
    # save PDF
    pdf_path = save_report_pdf(result)
    print(f"\nPDF exported → {pdf_path}")
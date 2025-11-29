"""
PACCS PDF Report Generator
Generates professional film analysis reports
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime


# Brand Colors
PURPLE = HexColor('#a855f7')
DARK_PURPLE = HexColor('#7c3aed')
DARK_BG = HexColor('#1a1a2e')
WHITE = HexColor('#ffffff')
GRAY = HexColor('#6b7280')
GREEN = HexColor('#22c55e')
YELLOW = HexColor('#f59e0b')


def generate_film_report(film_data, analysis_data, user_data=None):
    """
    Generate a PDF report for film analysis
    
    Args:
        film_data: dict with film info (title, genre, country, etc.)
        analysis_data: dict with analysis results (score, predictions, festivals, etc.)
        user_data: optional dict with user info
    
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=PURPLE,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=GRAY,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=DARK_PURPLE,
        spaceBefore=25,
        spaceAfter=15,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=DARK_BG,
        spaceAfter=10,
        leading=16
    )
    
    score_style = ParagraphStyle(
        'ScoreStyle',
        parent=styles['Normal'],
        fontSize=48,
        textColor=PURPLE,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Build content
    story = []
    
    # Header
    story.append(Paragraph("🎬 PACCS", title_style))
    story.append(Paragraph("AI Film Intelligence Report", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Film Title
    film_title = film_data.get('title', 'Untitled Film')
    story.append(Paragraph(f"<b>{film_title}</b>", ParagraphStyle(
        'FilmTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=DARK_BG,
        alignment=TA_CENTER,
        spaceAfter=10
    )))
    
    # Film Meta
    genre = film_data.get('genre', 'Unknown')
    country = film_data.get('country', 'Unknown')
    runtime = film_data.get('runtime', 'N/A')
    story.append(Paragraph(
        f"{genre} • {country} • {runtime}",
        ParagraphStyle('Meta', parent=body_style, alignment=TA_CENTER, textColor=GRAY)
    ))
    story.append(Spacer(1, 30))
    
    # Overall Score
    story.append(Paragraph("OVERALL SCORE", heading_style))
    score = analysis_data.get('score', 0)
    story.append(Paragraph(f"{score}/10", score_style))
    
    pathway = analysis_data.get('pathway', 'FESTIVAL')
    pathway_color = GREEN if pathway == 'THEATRICAL' else YELLOW
    story.append(Paragraph(
        f"Recommended Pathway: <b>{pathway}</b>",
        ParagraphStyle('Pathway', parent=body_style, alignment=TA_CENTER, textColor=pathway_color)
    ))
    story.append(Spacer(1, 20))
    
    # Predictions
    story.append(Paragraph("📊 SUCCESS PREDICTIONS", heading_style))
    
    predictions = analysis_data.get('predictions', {})
    pred_data = [
        ['Metric', 'Probability'],
        ['Festival Selection', f"{predictions.get('festival_selection', 0)}%"],
        ['Distribution Deal', f"{predictions.get('distribution_deal', 0)}%"],
        ['Award Nomination', f"{predictions.get('award_nomination', 0)}%"],
        ['Viral Potential', f"{predictions.get('viral_potential', 0)}%"],
    ]
    
    pred_table = Table(pred_data, colWidths=[10*cm, 5*cm])
    pred_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb')),
    ]))
    story.append(pred_table)
    story.append(Spacer(1, 20))
    
    # Festival Recommendations
    story.append(Paragraph("🏆 FESTIVAL RECOMMENDATIONS", heading_style))
    
    festivals = analysis_data.get('festivals', [])
    if festivals:
        fest_data = [['Festival', 'Match Score']]
        for fest in festivals[:5]:
            fest_data.append([fest.get('name', ''), f"{fest.get('score', 0)}%"])
        
        fest_table = Table(fest_data, colWidths=[10*cm, 5*cm])
        fest_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb')),
        ]))
        story.append(fest_table)
    story.append(Spacer(1, 20))
    
    # Distributor Recommendations
    story.append(Paragraph("🎬 DISTRIBUTOR MATCHES", heading_style))
    
    distributors = analysis_data.get('distributors', [])
    if distributors:
        dist_data = [['Distributor', 'Match Score']]
        for dist in distributors[:5]:
            dist_data.append([dist.get('name', ''), f"{dist.get('score', 0)}%"])
        
        dist_table = Table(dist_data, colWidths=[10*cm, 5*cm])
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), DARK_PURPLE),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb')),
        ]))
        story.append(dist_table)
    story.append(Spacer(1, 30))
    
    # Footer
    generated_date = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(
        f"Report generated on {generated_date}",
        ParagraphStyle('Footer', parent=body_style, alignment=TA_CENTER, textColor=GRAY, fontSize=9)
    ))
    story.append(Paragraph(
        "Powered by PACCS • paccs.peekaboon.com",
        ParagraphStyle('Footer2', parent=body_style, alignment=TA_CENTER, textColor=PURPLE, fontSize=10)
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_filmmaker_report(profile_data):
    """
    Generate a PDF profile/portfolio for a filmmaker
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=32,
        textColor=DARK_BG,
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=PURPLE,
        spaceAfter=5,
        alignment=TA_CENTER
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=11,
        textColor=DARK_BG,
        spaceAfter=10,
        leading=16
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=PURPLE,
        spaceBefore=20,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    story = []
    
    # Header
    story.append(Paragraph(profile_data.get('fullName', 'Filmmaker'), title_style))
    story.append(Paragraph(profile_data.get('designation', ''), subtitle_style))
    
    if profile_data.get('company'):
        story.append(Paragraph(profile_data.get('company'), ParagraphStyle(
            'Company', parent=body_style, alignment=TA_CENTER, textColor=GRAY
        )))
    
    location_parts = []
    if profile_data.get('city'):
        location_parts.append(profile_data.get('city'))
    if profile_data.get('country'):
        location_parts.append(profile_data.get('country'))
    if location_parts:
        story.append(Paragraph(' • '.join(location_parts), ParagraphStyle(
            'Location', parent=body_style, alignment=TA_CENTER, textColor=GRAY
        )))
    
    story.append(Spacer(1, 30))
    
    # Bio
    if profile_data.get('bio'):
        story.append(Paragraph("ABOUT", heading_style))
        story.append(Paragraph(profile_data.get('bio'), body_style))
    
    # Films
    film_links = profile_data.get('filmLinks', [])
    if film_links:
        story.append(Paragraph("FILMS", heading_style))
        for i, link in enumerate(film_links):
            if link:
                story.append(Paragraph(f"• Film {i+1}: {link}", body_style))
    
    # Social Links
    social_links = profile_data.get('socialLinks', {})
    active_links = {k: v for k, v in social_links.items() if v}
    if active_links:
        story.append(Paragraph("CONNECT", heading_style))
        for platform, url in active_links.items():
            story.append(Paragraph(f"• {platform.title()}: {url}", body_style))
    
    story.append(Spacer(1, 40))
    
    # Footer
    story.append(Paragraph(
        "Peekabooⁿ Club Member",
        ParagraphStyle('Footer', parent=body_style, alignment=TA_CENTER, textColor=PURPLE, fontSize=12)
    ))
    story.append(Paragraph(
        "paccs.peekaboon.com",
        ParagraphStyle('Footer2', parent=body_style, alignment=TA_CENTER, textColor=GRAY, fontSize=10)
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
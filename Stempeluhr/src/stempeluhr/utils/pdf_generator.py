from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from typing import List, Dict

def generate_monthly_report(
    vorname: str,
    nachname: str,
    jahr: int,
    monat: int,
    wochen_uebersichten: List[Dict],
    output_path: str
) -> str:
    """Generiert einen PDF-Bericht für die Monatsübersicht."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    
    # Elemente für den PDF
    elements = []
    
    # Titel
    monatsnamen = [
        "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember"
    ]
    title = f"Arbeitszeitübersicht - {monatsnamen[monat-1]} {jahr}"
    elements.append(Paragraph(title, title_style))
    
    # Mitarbeiterinformationen
    elements.append(Paragraph(f"Mitarbeiter: {vorname} {nachname}", styles['Normal']))
    elements.append(Paragraph(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Wochenübersicht
    data = [
        ['Kalenderwoche', 'Arbeitszeit (h)', 'Pausezeit (h)', 'Gesamtzeit (h)', 'Überstunden (h)']
    ]
    
    for uebersicht in wochen_uebersichten:
        data.append([
            str(uebersicht['woche']),
            f"{uebersicht['arbeitszeit']:.2f}",
            f"{uebersicht['pausezeit']:.2f}",
            f"{uebersicht['gesamtzeit']:.2f}",
            f"{uebersicht['ueberstunden']:.2f}"
        ])
    
    # Berechne Summen
    summen = [
        'Summe',
        f"{sum(w['arbeitszeit'] for w in wochen_uebersichten):.2f}",
        f"{sum(w['pausezeit'] for w in wochen_uebersichten):.2f}",
        f"{sum(w['gesamtzeit'] for w in wochen_uebersichten):.2f}",
        f"{sum(w['ueberstunden'] for w in wochen_uebersichten):.2f}"
    ]
    data.append(summen)
    
    # Tabelle erstellen
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    elements.append(table)
    
    # PDF generieren
    doc.build(elements)
    return output_path 
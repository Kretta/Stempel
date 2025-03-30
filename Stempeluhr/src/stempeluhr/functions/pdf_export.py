from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import datetime, timedelta
import calendar
import os

def get_weekday_name_de(date_str):
    """Konvertiert ein Datum in den deutschen Wochentag (Mo, Di, etc.)"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekdays = {
        0: 'Mo', 1: 'Di', 2: 'Mi', 3: 'Do', 
        4: 'Fr', 5: 'Sa', 6: 'So'
    }
    return weekdays[date_obj.weekday()]

def format_time(time_str):
    """Formatiert die Zeit von HH:MM:SS zu HH:MM"""
    if time_str:
        return time_str[:5]
    return ""

def create_monthly_pdf(db_handler, vorname: str, nachname: str, jahr: int, monat: int, output_path: str):
    """Erstellt eine PDF-Datei mit der Monatsübersicht"""
    # Hole alle Einträge für den Monat
    entries = db_handler.get_entries(vorname, nachname)
    
    # Filtere Einträge für den gewählten Monat
    month_entries = {}
    for entry in entries:
        entry_date = datetime.strptime(entry.date, "%Y-%m-%d")
        if entry_date.year == jahr and entry_date.month == monat:
            if entry.date not in month_entries:
                month_entries[entry.date] = {
                    'date': entry.date,
                    'anwesenheit': 'Betrieb',
                    'tag': get_weekday_name_de(entry.date),
                    'beginn': None,
                    'ende': None,
                    'pausen': [],
                    'stunden': '00:00'
                }
            
            if entry.status == "Ein":
                month_entries[entry.date]['beginn'] = format_time(entry.time)
            elif entry.status == "Aus":
                month_entries[entry.date]['ende'] = format_time(entry.time)
            elif entry.status == "Pause Start":
                month_entries[entry.date]['pausen'].append({'start': format_time(entry.time)})
            elif entry.status == "Pause Ende" and month_entries[entry.date]['pausen']:
                month_entries[entry.date]['pausen'][-1]['ende'] = format_time(entry.time)

    # Berechne die Arbeitszeit für jeden Tag
    for date_entry in month_entries.values():
        if date_entry['beginn'] and date_entry['ende']:
            beginn = datetime.strptime(date_entry['beginn'], "%H:%M")
            ende = datetime.strptime(date_entry['ende'], "%H:%M")
            total_pause = timedelta()
            
            for pause in date_entry['pausen']:
                if 'start' in pause and 'ende' in pause:
                    pause_start = datetime.strptime(pause['start'], "%H:%M")
                    pause_ende = datetime.strptime(pause['ende'], "%H:%M")
                    total_pause += pause_ende - pause_start
            
            arbeitszeit = ende - beginn - total_pause
            stunden = arbeitszeit.total_seconds() / 3600
            date_entry['stunden'] = f"{int(stunden):02d}:{int((stunden % 1) * 60):02d}"

    # Erstelle PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    # Definiere Stile
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=30
    )

    # Erstelle Dokumentinhalt
    elements = []
    
    # Titel
    month_name = calendar.month_name[monat]
    title = Paragraph(
        f"Arbeitszeiterfassung - {vorname} {nachname}<br/>"
        f"{month_name} {jahr}",
        title_style
    )
    elements.append(title)
    
    # Tabellendaten
    table_data = [
        ['Datum', 'Anwesenheit', 'Tag', 'Beginn', 'Ende', 'Pausen', 'Stunden']
    ]
    
    # Füge alle Tage des Monats hinzu
    _, last_day = calendar.monthrange(jahr, monat)
    for day in range(1, last_day + 1):
        date_str = f"{jahr}-{monat:02d}-{day:02d}"
        entry = month_entries.get(date_str, {
            'date': date_str,
            'anwesenheit': '',
            'tag': get_weekday_name_de(date_str),
            'beginn': '',
            'ende': '',
            'pausen': [],
            'stunden': '00:00'
        })
        
        # Formatiere Pausen
        pausen_str = ""
        for pause in entry['pausen']:
            if 'start' in pause and 'ende' in pause:
                pausen_str += f"{pause['start']}-{pause['ende']}\n"
        
        table_data.append([
            f"{day}.{monat}.{jahr}",
            entry['anwesenheit'],
            entry['tag'],
            entry['beginn'] or '',
            entry['ende'] or '',
            pausen_str.strip(),
            entry['stunden']
        ])
    
    # Erstelle Tabelle
    table = Table(table_data, colWidths=[2.5*cm, 3*cm, 1*cm, 2*cm, 2*cm, 3*cm, 2*cm])
    table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)
    
    # Füge Überstundenberechnung hinzu
    elements.append(Spacer(1, 30))
    
    # Berechne Überstunden
    wochen_uebersichten = db_handler.berechne_monatsuebersicht(vorname, nachname, jahr, monat)
    gesamt_ueberstunden = sum(w['ueberstunden'] for w in wochen_uebersichten)
    
    ueberstunden_text = Paragraph(
        f"Überstunden im {month_name} {jahr}: {gesamt_ueberstunden:.2f} Stunden",
        styles['Normal']
    )
    elements.append(ueberstunden_text)
    
    # Generiere PDF
    doc.build(elements)
    
    return output_path 
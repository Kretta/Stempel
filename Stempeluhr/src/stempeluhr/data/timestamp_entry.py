import os
import csv
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class timestamp_entry:
    vorname: str
    nachname: str
    date: str
    time: str
    status: str


def get_csv_filename():
    # Aktuelles Datum abrufen
    current_date = datetime.now()

    # Den ersten Tag des aktuellen Monats berechnen
    start_of_month = current_date.replace(day=1)
    month_start_str = start_of_month.strftime('%Y-%m-%d')

    # Pfad zum Dokumente-Ordner ermitteln (funktioniert auf deutsch/englisch)
    documents_folder = os.path.join(os.path.expanduser("~"), "Documents")
    
    # Logging des Speicherpfades
    logging.info(f"CSV-Datei wird in folgendem Ordner gespeichert: {documents_folder}")
    
    # CSV-Dateiname inklusive Pfad zum Dokumente-Ordner
    csv_filename = os.path.join(documents_folder, f'stempel_{month_start_str}.csv')

    return csv_filename




def create_timestamp_entry(entry: timestamp_entry):
    csv_filename = get_csv_filename()
    
    vorname = entry.vorname
    nachname = entry.nachname
    datum = entry.date
    uhrzeit = entry.time
    status = entry.status

    print(f'Speichern in CSV: {vorname}, {nachname}, {datum}, {uhrzeit}, {status}')
    file_exists = os.path.isfile(csv_filename)
    try:
        with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Vorname', 'Nachname', 'Datum', 'Uhrzeit', 'Ein/Aus'])
            writer.writerow([vorname, nachname, datum, uhrzeit, status])
        print(f'CSV-Datei erfolgreich aktualisiert: {csv_filename}')
    except Exception as e:
        print(f'Fehler beim Schreiben in die CSV-Datei: {e}')
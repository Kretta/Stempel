from ..models.time_entry import TimeEntry
from ..databaselogic.db_handler import DatabaseHandler

def load_history():
    try:
        db_handler = DatabaseHandler()
        entries = db_handler.get_entries()
        
        # Sortiere Einträge nach Datum und Zeit
        sorted_entries = sorted(
            entries,
            key=lambda x: (x.date, x.time),
            reverse=True  # Neueste zuerst
        )
        
        formatted_entries = []
        for entry in sorted_entries:
            # Formatiere die Daten für bessere Darstellung
            vorname = f"{entry.vorname:<15}"  # Linksbündig, 15 Zeichen
            nachname = f"{entry.nachname:<15}"  # Linksbündig, 15 Zeichen
            datum = f"{entry.date:^10}"  # Zentriert, 10 Zeichen
            zeit = f"{entry.time[:5]:^8}"  # Zentriert, 8 Zeichen (nur HH:MM)
            status = f"{entry.status:^7}"  # Zentriert, 7 Zeichen
            
            formatted_entries.append((
                vorname,
                nachname,
                datum,
                zeit,
                status
            ))
        return formatted_entries
    except Exception as e:
        print(f"Fehler beim Laden der Historie: {e}")
        return []

def get_last_entry():
    try:
        db_handler = DatabaseHandler()
        return db_handler.get_last_entry()
    except Exception as e:
        print(f"Fehler beim Laden des letzten Eintrags: {e}")
        return None 
from ..models.time_entry import TimeEntry
from .database import DatabaseHandler

def get_formatted_history(db_handler: DatabaseHandler):
    """Lädt und formatiert die Historie für die Anzeige"""
    try:
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

def get_last_user(db_handler: DatabaseHandler):
    """Holt den letzten Benutzer aus der Datenbank"""
    try:
        last_entry = db_handler.get_last_entry()
        if last_entry:
            return {
                'vorname': last_entry.vorname,
                'nachname': last_entry.nachname
            }
        return None
    except Exception as e:
        print(f"Fehler beim Laden des letzten Benutzers: {e}")
        return None 
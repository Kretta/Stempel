from ..models.time_entry import TimeEntry
from ..databaselogic.db_handler import DatabaseHandler
from typing import List
from datetime import datetime

def get_formatted_history(vorname: str = None, nachname: str = None) -> List[tuple]:
    """Holt und formatiert die Historie der Stempelzeiten."""
    try:
        db = DatabaseHandler()
        entries = db.get_entries(vorname, nachname)
        
        formatted_entries = []
        pause_times = {}  # Dictionary für Pausenzeiten pro Tag
        
        for entry in entries:
            try:
                # Berechne Pausenzeit
                pause_text = ""
                current_date = entry.date
                
                if entry.status == "Pause Ende":
                    if current_date in pause_times and pause_times[current_date]:
                        pause_start = datetime.strptime(pause_times[current_date], "%H:%M:%S")
                        pause_end = datetime.strptime(entry.time, "%H:%M:%S")
                        pause_duration = pause_end - pause_start
                        total_minutes = pause_duration.total_seconds() / 60
                        hours = int(total_minutes // 60)
                        minutes = int(total_minutes % 60)
                        
                        if hours > 0:
                            pause_text = f" ({hours}h {minutes}min)"
                        else:
                            pause_text = f" ({minutes}min)"
                        pause_times[current_date] = None  # Reset pause start time for this day
                
                elif entry.status == "Pause Start":
                    pause_times[current_date] = entry.time
                
                # Formatiere die Daten für die Tabelle
                status_text = f"{entry.status}{pause_text}"
                formatted_entry = (
                    f"{entry.vorname:<15}",  # Linksbündig, 15 Zeichen
                    f"{entry.nachname:<15}",  # Linksbündig, 15 Zeichen
                    f"{entry.date:^10}",      # Zentriert, 10 Zeichen
                    f"{entry.time[:5]:^8}",   # Zentriert, 8 Zeichen (nur HH:MM)
                    f"{status_text:<35}"      # Linksbündig, 35 Zeichen für Status und Pausenzeit
                )
                formatted_entries.append(formatted_entry)
            except Exception as e:
                print(f"Fehler beim Formatieren eines Eintrags: {e}")
                continue
                
        return formatted_entries
        
    except Exception as e:
        print(f"Fehler beim Laden der Historie: {e}")
        return []

def get_last_user(vorname: str = None, nachname: str = None):
    """Holt den letzten Benutzer aus der Datenbank"""
    try:
        db = DatabaseHandler()
        last_entry = db.get_last_entry(vorname, nachname)
        if last_entry:
            return {
                'vorname': last_entry.vorname,
                'nachname': last_entry.nachname
            }
        return None
    except Exception as e:
        print(f"Fehler beim Laden des letzten Benutzers: {e}")
        return None 
from datetime import datetime, timedelta
from ..models.time_entry import TimeEntry
from ..databaselogic.db_handler import DatabaseHandler
from ..utils.alerts import show_alert

def clock_in(vorname: str, nachname: str, window, db_handler: DatabaseHandler) -> bool:
    """Erfasst den Einstempelvorgang"""
    if not vorname or not nachname:
        show_alert(window, 'Fehler', 'Bitte Vor- und Nachnamen eingeben!')
        return False
    
    current_datetime = datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')

    entry = TimeEntry(vorname, nachname, date, time, 'Ein')
    return db_handler.save_entry(entry, None)

def clock_out(vorname: str, nachname: str, window, db_handler: DatabaseHandler) -> bool:
    """Erfasst den Ausstempelvorgang"""
    current_datetime = datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')

    entry = TimeEntry(vorname, nachname, date, time, 'Aus')
    return db_handler.save_entry(entry, None)

def start_break(vorname: str, nachname: str, window, db_handler: DatabaseHandler) -> bool:
    """Erfasst den Beginn einer Pause"""
    current_datetime = datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')

    entry = TimeEntry(vorname, nachname, date, time, 'Pause Start')
    return db_handler.save_entry(entry, None)

def end_break(vorname: str, nachname: str, window, db_handler: DatabaseHandler) -> bool:
    """Beendet die Pause für einen Benutzer."""
    try:
        # Hole den letzten Eintrag
        last_entry = db_handler.get_last_entry(vorname, nachname)
        if not last_entry or last_entry.status != "Pause Start":
            return False
            
        # Berechne Pausendauer
        current_time = datetime.now()
        pause_start = datetime.strptime(f"{last_entry.date} {last_entry.time}", "%Y-%m-%d %H:%M:%S")
        pause_end = datetime.strptime(f"{current_time.strftime('%Y-%m-%d')} {current_time.strftime('%H:%M:%S')}", "%Y-%m-%d %H:%M:%S")
        
        pause_duration = pause_end - pause_start
        total_minutes = pause_duration.total_seconds() / 60
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        
        if hours > 0:
            pause_dauer = f"{hours}h {minutes}min"
        else:
            pause_dauer = f"{minutes}min"
            
        # Erstelle neuen Eintrag
        entry = TimeEntry(
            vorname=vorname,
            nachname=nachname,
            date=current_time.strftime("%Y-%m-%d"),
            time=current_time.strftime("%H:%M:%S"),
            status="Pause Ende"
        )
        
        # Speichere Eintrag mit Pausendauer
        return db_handler.save_entry(entry, pause_dauer)
        
    except Exception as e:
        print(f"Fehler beim Beenden der Pause: {e}")
        return False 
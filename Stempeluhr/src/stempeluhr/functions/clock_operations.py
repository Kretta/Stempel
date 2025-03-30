from datetime import datetime
from ..models.time_entry import TimeEntry
from ..databaselogic.db_handler import DatabaseHandler
from ..utils.alerts import show_alert

def handle_clock_in(vorname: str, nachname: str, window) -> bool:
    if not vorname or not nachname:
        show_alert(window, 'Fehler', 'Bitte Vor- und Nachnamen eingeben!')
        return False
    
    current_datetime = datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')

    entry = TimeEntry(vorname, nachname, date, time, 'Ein')
    db_handler = DatabaseHandler()
    db_handler.save_entry(entry)
    return True

def handle_clock_out(vorname: str, nachname: str, window) -> bool:
    current_datetime = datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')

    entry = TimeEntry(vorname, nachname, date, time, 'Aus')
    db_handler = DatabaseHandler()
    db_handler.save_entry(entry)
    return True

def handle_pause_start(vorname: str, nachname: str, window) -> bool:
    current_datetime = datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')

    entry = TimeEntry(vorname, nachname, date, time, 'Pause Start')
    db_handler = DatabaseHandler()
    db_handler.save_entry(entry)
    return True

def handle_pause_end(vorname: str, nachname: str, window) -> bool:
    current_datetime = datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')

    entry = TimeEntry(vorname, nachname, date, time, 'Pause Ende')
    db_handler = DatabaseHandler()
    db_handler.save_entry(entry)
    return True 
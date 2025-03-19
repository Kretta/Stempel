from datetime import datetime
from ..models.time_entry import TimeEntry
from .database import DatabaseHandler
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
    db_handler.save_entry(entry)
    return True

def clock_out(vorname: str, nachname: str, window, db_handler: DatabaseHandler) -> bool:
    """Erfasst den Ausstempelvorgang"""
    current_datetime = datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')

    entry = TimeEntry(vorname, nachname, date, time, 'Aus')
    db_handler.save_entry(entry)
    return True

def start_break(vorname: str, nachname: str, window, db_handler: DatabaseHandler) -> bool:
    """Erfasst den Beginn einer Pause"""
    current_datetime = datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')

    entry = TimeEntry(vorname, nachname, date, time, 'Pause Start')
    db_handler.save_entry(entry)
    return True

def end_break(vorname: str, nachname: str, pause_duration: int, window, db_handler: DatabaseHandler) -> bool:
    """Erfasst das Ende einer Pause"""
    current_datetime = datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')

    status = f'Pause Ende ({pause_duration} Min.)' if pause_duration else 'Pause Ende (Dauer unbekannt)'
    entry = TimeEntry(vorname, nachname, date, time, status)
    db_handler.save_entry(entry)
    return True 
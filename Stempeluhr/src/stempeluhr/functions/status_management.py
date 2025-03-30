from datetime import datetime
from ..models.time_entry import TimeEntry
from ..databaselogic.db_handler import DatabaseHandler

def get_application_state(db_handler: DatabaseHandler, vorname: str = None, nachname: str = None) -> dict:
    """Holt den aktuellen Status der Anwendung."""
    try:
        if not vorname or not nachname:
            return {
                'is_clocked_in': False,
                'is_in_pause': False,
                'pause_start_time': None,
                'pause_button_text': 'Pause anfangen',
                'pause_button_enabled': False
            }
            
        # Hole den letzten Eintrag
        last_entry = db_handler.get_last_entry(vorname, nachname)
        
        if not last_entry:
            return {
                'is_clocked_in': False,
                'is_in_pause': False,
                'pause_start_time': None,
                'pause_button_text': 'Pause anfangen',
                'pause_button_enabled': False
            }
        
        # Bestimme den Status basierend auf dem letzten Eintrag
        if last_entry.status == 'Ein':
            return {
                'is_clocked_in': True,
                'is_in_pause': False,
                'pause_start_time': None,
                'pause_button_text': 'Pause anfangen',
                'pause_button_enabled': True
            }
        elif last_entry.status == 'Pause Start':
            return {
                'is_clocked_in': True,
                'is_in_pause': True,
                'pause_start_time': datetime.strptime(f"{last_entry.date} {last_entry.time}", "%Y-%m-%d %H:%M:%S"),
                'pause_button_text': 'Pause beenden',
                'pause_button_enabled': True
            }
        elif last_entry.status == 'Pause Ende':
            return {
                'is_clocked_in': True,
                'is_in_pause': False,
                'pause_start_time': None,
                'pause_button_text': 'Pause anfangen',
                'pause_button_enabled': True
            }
        elif last_entry.status == 'Aus':
            return {
                'is_clocked_in': False,
                'is_in_pause': False,
                'pause_start_time': None,
                'pause_button_text': 'Pause anfangen',
                'pause_button_enabled': False
            }
        else:
            return {
                'is_clocked_in': False,
                'is_in_pause': False,
                'pause_start_time': None,
                'pause_button_text': 'Pause anfangen',
                'pause_button_enabled': False
            }
    except Exception as e:
        print(f"Fehler beim Laden des Status: {e}")
        return None 
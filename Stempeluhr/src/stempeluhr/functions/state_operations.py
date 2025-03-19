from datetime import datetime
from ..models.time_entry import TimeEntry
from ..databaselogic.db_handler import DatabaseHandler

def restore_state():
    """Stellt den letzten Status der Anwendung wieder her"""
    try:
        db_handler = DatabaseHandler()
        last_entry = db_handler.get_last_entry()
        
        if last_entry:
            state = {
                'is_clocked_in': False,
                'is_in_pause': False,
                'pause_start_time': None,
                'pause_button_text': 'Pause anfangen',
                'pause_button_enabled': False
            }
            
            # Prüfe den letzten Status
            if last_entry.status == 'Ein':
                state['is_clocked_in'] = True
                state['pause_button_enabled'] = True
            elif last_entry.status == 'Pause Start':
                state['is_clocked_in'] = True
                state['is_in_pause'] = True
                state['pause_button_enabled'] = True
                state['pause_button_text'] = 'Pause beenden'
                # Setze die Startzeit der Pause
                time_parts = last_entry.time.split(':')
                date_parts = last_entry.date.split('-')
                state['pause_start_time'] = datetime(
                    int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
                    int(time_parts[0]), int(time_parts[1]), int(time_parts[2])
                )
            elif last_entry.status.startswith('Pause Ende') or last_entry.status == 'Aus':
                state['is_clocked_in'] = False
                state['is_in_pause'] = False
                state['pause_button_enabled'] = False
                state['pause_button_text'] = 'Pause anfangen'
                state['pause_start_time'] = None
            
            return state
        return None
    except Exception as e:
        print(f"Fehler beim Wiederherstellen des Status: {e}")
        return None 
from datetime import datetime
from ..database.db_handler import DatabaseHandler
from ..models.time_entry import TimeEntry

def create_timestamp_entry(entry: TimeEntry):
    db = DatabaseHandler()
    db.save_entry(entry)    
    print(f'Danke, dein Eintrag wurde in der Datenbank gespeichert.')
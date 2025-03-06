import sqlite3
import os
from pathlib import Path
from datetime import datetime
from ..models.time_entry import TimeEntry

class DatabaseHandler:
    def __init__(self):
        # Speicherort im Projektverzeichnis
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.db_path = os.path.join(project_root, 'database', 'stempeluhr.db')
        
        # Stelle sicher, dass das database Verzeichnis existiert
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        self.init_db()

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stempel (
                vorname TEXT,
                nachname TEXT,
                date TEXT,
                time TEXT,
                status TEXT
            )
        ''')
        self.conn.commit()

    def save_entry(self, entry: TimeEntry):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO stempel (vorname, nachname, date, time, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (entry.vorname, entry.nachname, entry.date, entry.time, entry.status))
        self.conn.commit()

    def get_entries(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM stempel ORDER BY date DESC, time DESC')
        rows = cursor.fetchall()
        return [TimeEntry(*row) for row in rows]

    def get_last_entry(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM stempel ORDER BY date DESC, time DESC LIMIT 1')
        row = cursor.fetchone()
        return TimeEntry(*row) if row else None
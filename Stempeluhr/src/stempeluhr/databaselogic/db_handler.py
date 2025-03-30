import sqlite3
import os
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from ..models.time_entry import TimeEntry

class DatabaseHandler:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseHandler, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialisiert die Datenbankverbindung"""
        # Verhindere mehrfache Initialisierung
        if hasattr(self, 'initialized'):
            return
            
        try:
            # Verwende den absoluten Pfad zur Datenbank im data Verzeichnis
            self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'stempeluhr.db')
            print(f"Verwende Datenbank: {self.db_path}")
            
            # Stelle Verbindung her und erstelle Tabelle falls nicht vorhanden
            self.conn = sqlite3.connect(self.db_path)
            self.init_db()
            print("Datenbank initialisiert")
            self.initialized = True
        except Exception as e:
            print(f"Fehler bei der Datenbankinitialisierung: {e}")
            raise

    def init_db(self):
        """Initialisiert die Datenbankstruktur"""
        try:
            cursor = self.conn.cursor()
            
            # Prüfe ob die pause_dauer Spalte existiert
            cursor.execute("PRAGMA table_info(stempel)")
            columns = cursor.fetchall()
            has_pause_dauer = any(column[1] == 'pause_dauer' for column in columns)
            
            if not has_pause_dauer:
                # Füge die neue Spalte hinzu
                cursor.execute("ALTER TABLE stempel ADD COLUMN pause_dauer TEXT")
                self.conn.commit()
                print("Spalte pause_dauer wurde hinzugefügt")
                
            # Erstelle Tabelle falls nicht vorhanden
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS stempel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vorname TEXT NOT NULL,
                nachname TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT NOT NULL,
                pause_dauer TEXT
            )
            """)
            self.conn.commit()
        except Exception as e:
            print(f"Fehler bei der Tabelleninitialisierung: {e}")
            raise

    def save_entry(self, entry: TimeEntry, pause_dauer: str = None) -> bool:
        """Speichert einen neuen Zeiteintrag in der Datenbank"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO stempel (vorname, nachname, date, time, status, pause_dauer)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (entry.vorname, entry.nachname, entry.date, entry.time, entry.status, pause_dauer))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Fehler beim Speichern des Eintrags: {e}")
            return False

    def get_entries(self, vorname: str = None, nachname: str = None) -> List[TimeEntry]:
        """Holt alle Einträge aus der Datenbank"""
        try:
            cursor = self.conn.cursor()
            if vorname and nachname:
                cursor.execute("""
                    SELECT vorname, nachname, date, time, status, pause_dauer
                    FROM stempel
                    WHERE vorname = ? AND nachname = ?
                    ORDER BY date DESC, time DESC
                """, (vorname, nachname))
            else:
                cursor.execute("""
                    SELECT vorname, nachname, date, time, status, pause_dauer
                    FROM stempel
                    ORDER BY date DESC, time DESC
                """)
            
            entries = []
            for row in cursor.fetchall():
                try:
                    entry = TimeEntry(
                        vorname=row[0],
                        nachname=row[1],
                        date=row[2],
                        time=row[3],
                        status=row[4]
                    )
                    entries.append(entry)
                except Exception as e:
                    print(f"Fehler beim Verarbeiten eines Eintrags: {e}")
                    continue
            return entries
        except Exception as e:
            print(f"Fehler beim Laden der Einträge: {e}")
            return []

    def get_last_entry(self, vorname: str = None, nachname: str = None) -> Optional[TimeEntry]:
        """Holt den letzten Eintrag aus der Datenbank"""
        try:
            cursor = self.conn.cursor()
            if vorname and nachname:
                cursor.execute("""
                    SELECT vorname, nachname, date, time, status, pause_dauer
                    FROM stempel
                    WHERE vorname = ? AND nachname = ?
                    ORDER BY date DESC, time DESC
                    LIMIT 1
                """, (vorname, nachname))
            else:
                cursor.execute("""
                    SELECT vorname, nachname, date, time, status, pause_dauer
                    FROM stempel
                    ORDER BY date DESC, time DESC
                    LIMIT 1
                """)
            
            row = cursor.fetchone()
            if row:
                return TimeEntry(
                    vorname=row[0],
                    nachname=row[1],
                    date=row[2],
                    time=row[3],
                    status=row[4]
                )
            return None
        except Exception as e:
            print(f"Fehler beim Laden des letzten Eintrags: {e}")
            return None

    def get_wochennummer(self, datum: datetime) -> int:
        """Berechnet die Kalenderwoche für ein Datum."""
        return datum.isocalendar()[1]

    def berechne_monatsuebersicht(self, vorname: str, nachname: str, jahr: int, monat: int) -> List[Dict]:
        """Berechnet die Arbeitszeit pro Woche für einen bestimmten Monat."""
        entries = self.get_entries(vorname, nachname)
        
        # Filtere Einträge für den gewählten Monat
        monats_eintraege = [
            e for e in entries 
            if datetime.strptime(e.date, "%Y-%m-%d").year == jahr and 
               datetime.strptime(e.date, "%Y-%m-%d").month == monat
        ]
        
        # Gruppiere Einträge nach Wochen
        wochen_eintraege = {}
        for eintrag in monats_eintraege:
            datum = datetime.strptime(eintrag.date, "%Y-%m-%d")
            woche = self.get_wochennummer(datum)
            if woche not in wochen_eintraege:
                wochen_eintraege[woche] = []
            wochen_eintraege[woche].append(eintrag)
        
        # Berechne Zeiten pro Woche
        wochen_uebersichten = []
        for woche, eintraege in wochen_eintraege.items():
            arbeitszeit = timedelta()
            pausezeit = timedelta()
            letzter_kommen = None
            letzter_pause_start = None
            
            for eintrag in eintraege:
                zeit = datetime.strptime(f"{eintrag.date} {eintrag.time}", "%Y-%m-%d %H:%M:%S")
                
                if eintrag.status == "Ein":
                    letzter_kommen = zeit
                elif eintrag.status == "Aus" and letzter_kommen:
                    arbeitszeit += zeit - letzter_kommen
                elif eintrag.status == "Pause Start":
                    letzter_pause_start = zeit
                elif eintrag.status == "Pause Ende" and letzter_pause_start:
                    pausezeit += zeit - letzter_pause_start
            
            gesamtzeit = arbeitszeit - pausezeit
            gesamtstunden = gesamtzeit.total_seconds() / 3600
            
            # Berechne Überstunden (mehr als 40 Stunden pro Woche)
            ueberstunden = max(0, gesamtstunden - 40)
            
            wochen_uebersichten.append({
                "woche": woche,
                "arbeitszeit": arbeitszeit.total_seconds() / 3600,
                "pausezeit": pausezeit.total_seconds() / 3600,
                "gesamtzeit": gesamtstunden,
                "ueberstunden": ueberstunden
            })
        
        # Sortiere nach Kalenderwoche
        wochen_uebersichten.sort(key=lambda x: x["woche"])
        
        return wochen_uebersichten 
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from datetime import datetime
import logging
from ..models.time_entry import TimeEntry
from ..databaselogic.db_handler import DatabaseHandler
from ..utils.alerts import show_alert, show_confirmation

class StempelUhrElement:
    def __init__(self, element_id: str):
        self.card_id = element_id
        self.is_clocked_in = False
        self.is_in_pause = False
        self.pause_start_time = None
        self.name_changed = False
        self.last_vorname = ""
        self.last_nachname = ""
        self.db_handler = DatabaseHandler()
        self.card = self.create_card()
        self.load_history()
        self.restore_state()
        self.load_last_user()

    def create_card(self):
        # Erstelle einen Container für die Eingabefelder
        self.vorname_input = toga.TextInput(
            placeholder="Vorname",
            style=Pack(width=200, padding=(5, 10))
        )
        self.nachname_input = toga.TextInput(
            placeholder="Nachname",
            style=Pack(width=200, padding=(5, 10))
        )

        input_container = toga.Box(
            children=[
                toga.Box(
                    children=[
                        self.vorname_input,
                        self.nachname_input
                    ],
                    style=Pack(direction=ROW, padding=(5, 0))
                )
            ],
            style=Pack(direction=COLUMN)
        )

        current_time = datetime.now().strftime("%H:%M")
        self.time_label = toga.Label(
            f"Aktuelle Zeit: {current_time}",
            style=Pack(padding=(5, 10))
        )

        # Erstelle die Buttons
        self.clock_in_button = toga.Button(
            'Kommen',
            style=Pack(padding=(5, 10), width=200),
            on_press=self.on_kommen_press
        )
        
        self.pause_button = toga.Button(
            'Pause anfangen',
            style=Pack(padding=(5, 10), width=200),
            on_press=self.on_pause_press
        )
        self.pause_button.enabled = False  # Initial deaktiviert
        
        self.clock_out_button = toga.Button(
            'Gehen',
            style=Pack(padding=(5, 10), width=200),
            on_press=self.on_gehen_press
        )

        button_box = toga.Box(
            children=[self.clock_in_button, self.pause_button, self.clock_out_button],
            style=Pack(direction=ROW, padding=(5, 10))
        )

        # Erstelle die Tabelle mit festen Spaltenbreiten
        self.table = toga.Table(
            headings=['Vorname', 'Nachname', 'Datum', 'Uhrzeit', 'Ein/Aus'],
            missing_value='',
            style=Pack(width=580)  # Feste Gesamtbreite
        )

        # Container für die Tabelle mit fester Höhe
        table_box = toga.Box(
            children=[self.table],
            style=Pack(
                padding=5,
                width=580,  # Feste Breite
                height=300  # Feste Höhe
            )
        )

        # Hauptcontainer
        box = toga.Box(
            children=[
                input_container,
                self.time_label,
                button_box,
                table_box
            ],
            style=Pack(
                direction=COLUMN,
                padding=10,
                alignment=CENTER
            )
        )

        return box

    def load_history(self):
        try:
            entries = self.db_handler.get_entries()
            self.table.data.clear()
            
            # Sortiere Einträge nach Datum und Zeit
            sorted_entries = sorted(
                entries,
                key=lambda x: (x.date, x.time),
                reverse=True  # Neueste zuerst
            )
            
            for entry in sorted_entries:
                # Formatiere die Daten für bessere Darstellung
                vorname = f"{entry.vorname:<15}"  # Linksbündig, 15 Zeichen
                nachname = f"{entry.nachname:<15}"  # Linksbündig, 15 Zeichen
                datum = f"{entry.date:^10}"  # Zentriert, 10 Zeichen
                zeit = f"{entry.time[:5]:^8}"  # Zentriert, 8 Zeichen (nur HH:MM)
                status = f"{entry.status:^7}"  # Zentriert, 7 Zeichen
                
                self.table.data.append((
                    vorname,
                    nachname,
                    datum,
                    zeit,
                    status
                ))
            logging.info(f"{len(entries)} Einträge aus der Historie geladen")
        except Exception as e:
            logging.error(f"Fehler beim Laden der Historie: {e}")

    def load_last_user(self):
        try:
            last_entry = self.db_handler.get_last_entry()
            if last_entry:
                self.update_user_info(last_entry.vorname, last_entry.nachname)
                logging.info(f"Letzter Benutzer geladen: {last_entry.vorname} {last_entry.nachname}")
        except Exception as e:
            logging.error(f"Fehler beim Laden des letzten Benutzers: {e}")

    def update_user_info(self, vorname, nachname):
        self.vorname_input.value = vorname
        self.nachname_input.value = nachname
        self.last_vorname = vorname
        self.last_nachname = nachname
        logging.info(f"User info set to: {vorname} {nachname}")

    def restore_state(self):
        """Stellt den letzten Status der Anwendung wieder her"""
        try:
            last_entry = self.db_handler.get_last_entry()
            if last_entry:
                # Prüfe den letzten Status
                if last_entry.status == 'Ein':
                    self.is_clocked_in = True
                    self.pause_button.enabled = True
                elif last_entry.status == 'Pause Start':
                    self.is_clocked_in = True
                    self.is_in_pause = True
                    self.pause_button.enabled = True
                    self.pause_button.text = 'Pause beenden'
                    # Setze die Startzeit der Pause
                    time_parts = last_entry.time.split(':')
                    date_parts = last_entry.date.split('-')
                    self.pause_start_time = datetime(
                        int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
                        int(time_parts[0]), int(time_parts[1]), int(time_parts[2])
                    )
                elif last_entry.status.startswith('Pause Ende') or last_entry.status == 'Aus':
                    self.is_clocked_in = False
                    self.is_in_pause = False
                    self.pause_button.enabled = False
                    self.pause_button.text = 'Pause anfangen'
                    self.pause_start_time = None
                
                logging.info(f"Status wiederhergestellt: Eingestempelt={self.is_clocked_in}, In Pause={self.is_in_pause}")
        except Exception as e:
            logging.error(f"Fehler beim Wiederherstellen des Status: {e}")

    async def on_pause_press(self, widget):
        if not self.is_clocked_in:
            show_alert(self.vorname_input.window, 'Fehler', 'Sie müssen zuerst einstempeln!')
            return

        current_datetime = datetime.now()
        
        if not self.is_in_pause:
            # Pause starten
            self.is_in_pause = True
            self.pause_start_time = current_datetime
            self.pause_button.text = 'Pause beenden'
            self._handle_clock_event('Pause Start')
        else:
            # Pause beenden und Dauer berechnen
            self.is_in_pause = False
            if self.pause_start_time:  # Prüfe ob Startzeit existiert
                pause_duration = current_datetime - self.pause_start_time
                pause_minutes = int(pause_duration.total_seconds() / 60)
                self.pause_button.text = 'Pause anfangen'
                self._handle_clock_event(f'Pause Ende ({pause_minutes} Min.)')
            else:
                # Falls keine Startzeit verfügbar ist
                self.pause_button.text = 'Pause anfangen'
                self._handle_clock_event('Pause Ende (Dauer unbekannt)')
            self.pause_start_time = None

    async def on_kommen_press(self, widget):
        if self.is_clocked_in:
            show_alert(self.vorname_input.window, 'Fehler', 'Sie sind bereits eingestempelt!')
        else:
            vorname = self.vorname_input.value
            nachname = self.nachname_input.value
            if not vorname or not nachname:
                show_alert(self.vorname_input.window, 'Fehler', 'Bitte Vor- und Nachnamen eingeben!')
                return
            
            self._handle_clock_event('Ein')
            self.is_clocked_in = True
            self.pause_button.enabled = True  # Aktiviere Pause-Button

    def on_gehen_press(self, widget):
        if not self.is_clocked_in:
            show_alert(self.vorname_input.window, 'Fehler', 'Sie sind nicht eingestempelt!')
        elif self.is_in_pause:
            show_alert(self.vorname_input.window, 'Fehler', 'Bitte beenden Sie zuerst Ihre Pause!')
        else:
            self._handle_clock_event('Aus')
            self.is_clocked_in = False
            self.pause_button.enabled = False  # Deaktiviere Pause-Button
            self.pause_button.text = 'Pause anfangen'  # Reset Pause-Button Text

    def _handle_clock_event(self, status: str):
        vorname = self.vorname_input.value
        nachname = self.nachname_input.value
        current_datetime = datetime.now()
        date = current_datetime.strftime('%Y-%m-%d')
        time = current_datetime.strftime('%H:%M:%S')

        entry = TimeEntry(vorname, nachname, date, time, status)
        self.db_handler.save_entry(entry)
        
        # Lade die komplette Historie neu, um die korrekte Sortierung zu gewährleisten
        self.load_history()

    def get_card(self):
        return self.card
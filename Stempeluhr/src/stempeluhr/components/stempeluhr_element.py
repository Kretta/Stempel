import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from datetime import datetime
import logging
from ..models.time_entry import TimeEntry
from ..database.db_handler import DatabaseHandler
from ..utils.alerts import show_alert, show_confirmation

class StempelUhrElement:
    def __init__(self, element_id: str):
        self.card_id = element_id
        self.is_clocked_in = False
        self.name_changed = False
        self.last_vorname = ""
        self.last_nachname = ""
        self.db_handler = DatabaseHandler()
        self.card = self.create_card()
        self.load_last_user()

    def create_card(self):
        self.vorname_input = toga.TextInput(placeholder="Vorname", style=Pack(padding=10))
        self.nachname_input = toga.TextInput(placeholder="Nachname", style=Pack(padding=10))

        current_time = datetime.now().strftime("%H:%M")
        self.time_label = toga.Label(f"Aktuelle Zeit: {current_time}", style=Pack(padding=10))

        self.clock_in_button = toga.Button('Kommen', style=Pack(padding=10), on_press=self.on_kommen_press)
        self.clock_out_button = toga.Button('Gehen', style=Pack(padding=10), on_press=self.on_gehen_press)

        self.table = toga.Table(
            headings=['Vorname', 'Nachname', 'Datum', 'Uhrzeit', 'Ein/Aus'], 
            style=Pack(flex=1)
        )

        button_box = toga.Box(children=[self.clock_in_button, self.clock_out_button], style=Pack(direction=ROW, padding=10))
        
        box = toga.Box(
            children=[self.vorname_input, self.nachname_input, self.time_label, button_box, self.table],
            style=Pack(direction=COLUMN, alignment=CENTER, padding=10)
        )

        return box

    def load_last_user(self):
        try:
            entries = self.db_handler.get_entries()
            if entries:
                last_entry = entries[0]
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

    def on_gehen_press(self, widget):
        if not self.is_clocked_in:
            show_alert(self.vorname_input.window, 'Fehler', 'Sie sind nicht eingestempelt!')
        else:
            self._handle_clock_event('Aus')
            self.is_clocked_in = False

    def _handle_clock_event(self, status: str):
        vorname = self.vorname_input.value
        nachname = self.nachname_input.value
        current_datetime = datetime.now()
        date = current_datetime.strftime('%Y-%m-%d')
        time = current_datetime.strftime('%H:%M:%S')

        entry = TimeEntry(vorname, nachname, date, time, status)
        self.db_handler.save_entry(entry)
        
        self.table.data.append((vorname, nachname, date, time, status))


    def get_card(self):
        return self.card
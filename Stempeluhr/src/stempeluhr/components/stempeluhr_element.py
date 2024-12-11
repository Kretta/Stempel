import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from datetime import datetime
import csv
import os
import logging
from ..data.timestamp_entry import create_timestamp_entry, timestamp_entry, get_csv_filename
from ..utils.alerts import show_alert, show_confirmation


class StempelUhrElement:
    def __init__(self, element_id: str):
        self.card_id = element_id
        self.is_clocked_in = False
        self.name_changed = False
        self.last_vorname = ""
        self.last_nachname = ""
        self.card = self.create_card()
        self.load_last_user()

    def create_card(self):
        self.vorname_input = toga.TextInput(placeholder="Vorname", style=Pack(padding=10))
        self.nachname_input = toga.TextInput(placeholder="Nachname", style=Pack(padding=10))

        current_time = datetime.now().strftime("%H:%M")
        self.time_label = toga.Label(f"Aktuelle Zeit: {current_time}", style=Pack(padding=10))

        self.clock_in_button = toga.Button('Kommen', style=Pack(padding=10), on_press=self.set_clock_in)
        self.clock_out_button = toga.Button('Gehen', style=Pack(padding=10), on_press=self.set_clock_out)

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
        csv_file = get_csv_filename()
        logging.info(f"Versuche, letzten Benutzer aus {csv_file} zu laden")
        
        # If file doesn't exist, just return without error
        if not os.path.exists(csv_file):
            logging.info(f"CSV-Datei {csv_file} existiert noch nicht")
            return
            
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                last_row = None
                for row in reader:
                    if len(row) >= 2:
                        last_row = row
                if last_row:
                    self.update_user_info(last_row[0], last_row[1])
                    logging.info(f"Benutzerinfo aktualisiert: {last_row[0]} {last_row[1]}")
                else:
                    logging.warning("Keine gültigen Zeilen in der CSV-Datei gefunden")
        except Exception as e:
            logging.error(f"Fehler beim Laden des letzten Benutzers: {e}")

    def update_user_info(self, vorname, nachname):
        self.vorname_input.value = vorname
        self.nachname_input.value = nachname
        self.last_vorname = vorname
        self.last_nachname = nachname
        logging.info(f"User info set to: {vorname} {nachname}")
    
    def get_card(self):
        return self.card

    async def set_clock_in(self, widget):
        if self.is_clocked_in:
            show_alert(self.vorname_input.window, 'Fehler', 'Sie sind bereits eingestempelt!')
        else:
            vorname = self.vorname_input.value
            nachname = self.nachname_input.value
            if not vorname or not nachname:
                show_alert(self.vorname_input.window, 'Fehler', 'Bitte Vor- und Nachnamen eingeben!')
                return
            
            if vorname != self.last_vorname or nachname != self.last_nachname:
                confirmation = await show_confirmation(self.vorname_input.window, 'Bestätigung', 'Möchten Sie den geänderten Namen auch in der CSV-Datei aktualisieren?')
                if confirmation:
                    self.update_csv_name(vorname, nachname)
                self.last_vorname = vorname
                self.last_nachname = nachname
            
            self._handle_clock_event('Ein')
            self.is_clocked_in = True

    def set_clock_out(self, widget):
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

        self.table.data.append((vorname, nachname, date, time, status))

        entry = timestamp_entry(vorname, nachname, date, time, status)
        create_timestamp_entry(entry)

    def update_csv_name(self, new_vorname, new_nachname):
        csv_file = get_csv_filename()
        temp_file = csv_file + '.temp'
        current_datetime = datetime.now()
        date = current_datetime.strftime('%Y-%m-%d')
        time = current_datetime.strftime('%H:%M:%S')
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(csv_file), exist_ok=True)
        
        # If file doesn't exist, create it with header
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Vorname', 'Nachname', 'Datum', 'Uhrzeit', 'Status'])
                writer.writerow([new_vorname, new_nachname, date, time, 'Neu'])
                logging.info(f"Neue CSV-Datei erstellt: {csv_file}")
            return

        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as file, \
                 open(temp_file, 'w', newline='', encoding='utf-8') as temp:
                reader = csv.reader(file)
                writer = csv.writer(temp)
                
                for row in reader:
                    writer.writerow(row)
                
                # Füge eine neue Zeile mit dem geänderten Namen und der aktuellen Zeit hinzu
                writer.writerow([new_vorname, new_nachname, date, time, 'Namensänderung'])
            
            os.replace(temp_file, csv_file)
            logging.info(f"CSV-Datei aktualisiert mit neuem Namen und Zeitstempel: {new_vorname} {new_nachname}, {date} {time}")
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            logging.error(f"Fehler beim Aktualisieren der CSV-Datei: {e}")
            raise

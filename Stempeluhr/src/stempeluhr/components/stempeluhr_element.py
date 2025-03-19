import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from datetime import datetime
import logging
from ..functions.time_tracking import clock_in, clock_out, start_break, end_break
from ..functions.data_display import get_formatted_history, get_last_user
from ..functions.status_management import get_application_state
from ..utils.alerts import show_alert
from ..functions.database import DatabaseHandler

class StempelUhrElement:
    def __init__(self, element_id: str, db_handler: DatabaseHandler):
        self.card_id = element_id
        self.db_handler = db_handler
        self.is_clocked_in = False
        self.is_in_pause = False
        self.pause_start_time = None
        self.name_changed = False
        self.last_vorname = ""
        self.last_nachname = ""
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
        self.pause_button.enabled = False
        
        self.clock_out_button = toga.Button(
            'Gehen',
            style=Pack(padding=(5, 10), width=200),
            on_press=self.on_gehen_press
        )

        button_box = toga.Box(
            children=[self.clock_in_button, self.pause_button, self.clock_out_button],
            style=Pack(direction=ROW, padding=(5, 10))
        )

        # Erstelle die Tabelle mit automatischer Skalierung
        self.table = toga.Table(
            headings=['Vorname', 'Nachname', 'Datum', 'Uhrzeit', 'Ein/Aus'],
            missing_value='',
            style=Pack(flex=1)
        )

        # Container für die Tabelle mit automatischer Skalierung
        table_box = toga.Box(
            children=[self.table],
            style=Pack(
                padding=5,
                flex=1
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
                alignment=CENTER,
                flex=1
            )
        )

        return box

    def load_history(self):
        self.table.data.clear()
        self.table.data = get_formatted_history(self.db_handler)

    def load_last_user(self):
        last_user = get_last_user(self.db_handler)
        if last_user:
            self.update_user_info(last_user['vorname'], last_user['nachname'])

    def update_user_info(self, vorname, nachname):
        self.vorname_input.value = vorname
        self.nachname_input.value = nachname
        self.last_vorname = vorname
        self.last_nachname = nachname

    def restore_state(self):
        state = get_application_state(self.db_handler)
        if state:
            self.is_clocked_in = state['is_clocked_in']
            self.is_in_pause = state['is_in_pause']
            self.pause_start_time = state['pause_start_time']
            self.pause_button.text = state['pause_button_text']
            self.pause_button.enabled = state['pause_button_enabled']

    async def on_pause_press(self, widget):
        if not self.is_clocked_in:
            show_alert(self.vorname_input.window, 'Fehler', 'Sie müssen zuerst einstempeln!')
            return

        current_datetime = datetime.now()
        vorname = self.vorname_input.value
        nachname = self.nachname_input.value
        
        if not self.is_in_pause:
            # Pause starten
            if start_break(vorname, nachname, self.vorname_input.window, self.db_handler):
                self.is_in_pause = True
                self.pause_start_time = current_datetime
                self.pause_button.text = 'Pause beenden'
                self.load_history()
        else:
            # Pause beenden und Dauer berechnen
            pause_duration = None
            if self.pause_start_time:
                pause_duration = int((current_datetime - self.pause_start_time).total_seconds() / 60)
            
            if end_break(vorname, nachname, pause_duration, self.vorname_input.window, self.db_handler):
                self.is_in_pause = False
                self.pause_button.text = 'Pause anfangen'
                self.pause_start_time = None
                self.load_history()

    async def on_kommen_press(self, widget):
        if self.is_clocked_in:
            show_alert(self.vorname_input.window, 'Fehler', 'Sie sind bereits eingestempelt!')
        else:
            vorname = self.vorname_input.value
            nachname = self.nachname_input.value
            if clock_in(vorname, nachname, self.vorname_input.window, self.db_handler):
                self.is_clocked_in = True
                self.pause_button.enabled = True
                self.load_history()

    def on_gehen_press(self, widget):
        if not self.is_clocked_in:
            show_alert(self.vorname_input.window, 'Fehler', 'Sie sind nicht eingestempelt!')
        elif self.is_in_pause:
            show_alert(self.vorname_input.window, 'Fehler', 'Bitte beenden Sie zuerst Ihre Pause!')
        else:
            vorname = self.vorname_input.value
            nachname = self.nachname_input.value
            if clock_out(vorname, nachname, self.vorname_input.window, self.db_handler):
                self.is_clocked_in = False
                self.pause_button.enabled = False
                self.pause_button.text = 'Pause anfangen'
                self.load_history()

    def get_card(self):
        return self.card

    async def show_about(self, widget):
        """Zeigt Informationen über die App an"""
        self.vorname_input.window.info_dialog(
            'Über Stempeluhr',
            'Stempeluhr - Eine Zeiterfassungsanwendung'
        )

    async def exit_app(self, widget):
        """Beendet die Anwendung"""
        if self.vorname_input.window.question_dialog(
            'Beenden',
            'Möchten Sie die Anwendung wirklich beenden?'
        ):
            self.vorname_input.window.app.exit()
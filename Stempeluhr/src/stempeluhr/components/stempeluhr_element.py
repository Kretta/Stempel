import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from datetime import datetime
import logging
from ..functions.time_tracking import clock_in, clock_out, start_break, end_break
from ..functions.data_display import get_formatted_history, get_last_user
from ..functions.status_management import get_application_state
from ..utils.alerts import show_alert
from ..databaselogic.db_handler import DatabaseHandler
import os

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
        # Lade zuerst den letzten Benutzer
        self.load_last_user()
        # Dann lade die Historie und den Status
        self.load_history()
        self.restore_state()

    def create_card(self):
        # Erstelle einen Container für die Eingabefelder
        self.vorname_input = toga.TextInput(
            placeholder="Vorname",
            style=Pack(width=200, padding=(5, 10)),
            on_change=self.on_name_change
        )
        self.nachname_input = toga.TextInput(
            placeholder="Nachname",
            style=Pack(width=200, padding=(5, 10)),
            on_change=self.on_name_change
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

        # Neue Buttons für Monatsübersicht und PDF-Export
        self.monatsuebersicht_button = toga.Button(
            'Monatsübersicht',
            style=Pack(padding=(5, 10), width=200),
            on_press=self.on_monatsuebersicht_press
        )

        self.pdf_export_button = toga.Button(
            'PDF Export',
            style=Pack(padding=(5, 10), width=200),
            on_press=self.on_pdf_export_press
        )

        button_box = toga.Box(
            children=[
                self.clock_in_button,
                self.pause_button,
                self.clock_out_button,
                self.monatsuebersicht_button,
                self.pdf_export_button
            ],
            style=Pack(direction=ROW, padding=(5, 10))
        )

        # Erstelle die Tabelle mit automatischer Skalierung
        self.table = toga.Table(
            headings=['Vorname', 'Nachname', 'Datum', 'Uhrzeit', 'Status (Pause)'],
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

    def on_name_change(self, widget):
        """Wird aufgerufen, wenn sich der Name ändert"""
        if self.vorname_input.value != self.last_vorname or self.nachname_input.value != self.last_nachname:
            self.name_changed = True
            self.last_vorname = self.vorname_input.value
            self.last_nachname = self.nachname_input.value
            # Lade die Historie für den neuen Benutzer
            self.load_history()
            self.restore_state()

    def load_history(self):
        """Lädt die Historie für den aktuellen Benutzer"""
        vorname = self.vorname_input.value
        nachname = self.nachname_input.value
        self.table.data.clear()
        
        try:
            # Lade Historie für den aktuellen Benutzer
            self.table.data = get_formatted_history(vorname, nachname)
        except Exception as e:
            print(f"Fehler beim Laden der Historie: {e}")
            self.table.data = []

    def load_last_user(self):
        """Lädt den letzten Benutzer"""
        try:
            # Hole den letzten Benutzer
            last_user = get_last_user()
            if last_user:
                self.update_user_info(last_user['vorname'], last_user['nachname'])
                # Lade die Historie für den gefundenen Benutzer
                self.load_history()
                # Stelle den Status wieder her
                self.restore_state()
        except Exception as e:
            print(f"Fehler beim Laden des letzten Benutzers: {e}")

    def update_user_info(self, vorname, nachname):
        """Aktualisiert die Benutzerinformationen"""
        self.vorname_input.value = vorname
        self.nachname_input.value = nachname
        self.last_vorname = vorname
        self.last_nachname = nachname
        self.name_changed = False

    def restore_state(self):
        vorname = self.vorname_input.value
        nachname = self.nachname_input.value
        state = get_application_state(self.db_handler, vorname, nachname)
        if state:
            self.is_clocked_in = state['is_clocked_in']
            self.is_in_pause = state['is_in_pause']
            self.pause_start_time = state['pause_start_time']
            self.pause_button.text = state['pause_button_text']
            self.pause_button.enabled = state['pause_button_enabled']

    def on_pause_press(self, button):
        """Behandelt das Drücken des Pause-Buttons"""
        vorname = self.vorname_input.value.strip()
        nachname = self.nachname_input.value.strip()
        
        if not vorname or not nachname:
            show_alert(self.vorname_input.window, 'Fehler', 'Bitte Vor- und Nachnamen eingeben!')
            return
        
        last_entry = self.db_handler.get_last_entry(vorname, nachname)
        if not last_entry:
            if start_break(vorname, nachname, self.vorname_input.window, self.db_handler):
                self.load_history()
                self.load_last_user()
        else:
            if last_entry.status == "Pause Start":
                if end_break(vorname, nachname, self.vorname_input.window, self.db_handler):
                    self.load_history()
                    self.load_last_user()
            else:
                if start_break(vorname, nachname, self.vorname_input.window, self.db_handler):
                    self.load_history()
                    self.load_last_user()

    async def on_kommen_press(self, widget):
        if self.is_clocked_in:
            show_alert(self.vorname_input.window, 'Fehler', 'Sie sind bereits eingestempelt!')
        else:
            vorname = self.vorname_input.value
            nachname = self.nachname_input.value
            if clock_in(vorname, nachname, self.vorname_input.window, self.db_handler):
                self.load_history()
                self.load_last_user()
                self.restore_state()

    def on_gehen_press(self, widget):
        if not self.is_clocked_in:
            show_alert(self.vorname_input.window, 'Fehler', 'Sie sind nicht eingestempelt!')
        elif self.is_in_pause:
            show_alert(self.vorname_input.window, 'Fehler', 'Bitte beenden Sie zuerst Ihre Pause!')
        else:
            vorname = self.vorname_input.value
            nachname = self.nachname_input.value
            if clock_out(vorname, nachname, self.vorname_input.window, self.db_handler):
                self.load_history()
                self.load_last_user()
                self.restore_state()

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

    async def on_monatsuebersicht_press(self, widget):
        """Zeigt die Monatsübersicht an."""
        vorname = self.vorname_input.value
        nachname = self.nachname_input.value
        
        if not vorname or not nachname:
            show_alert(self.vorname_input.window, 'Fehler', 'Bitte geben Sie Vor- und Nachname ein.')
            return
        
        # Aktuelles Datum
        jetzt = datetime.now()
        jahr = jetzt.year
        monat = jetzt.month
        
        # Berechne und speichere die Übersicht
        wochen_uebersichten = self.db_handler.speichere_monatsuebersicht(vorname, nachname, jahr, monat)
        
        # Erstelle die Nachricht
        nachricht = "Monatsübersicht:\n\n"
        for woche in wochen_uebersichten:
            nachricht += f"Kalenderwoche {woche['woche']}:\n"
            nachricht += f"Arbeitszeit: {woche['arbeitszeit']:.2f} Stunden\n"
            nachricht += f"Pausezeit: {woche['pausezeit']:.2f} Stunden\n"
            nachricht += f"Gesamtzeit: {woche['gesamtzeit']:.2f} Stunden\n"
            nachricht += f"Überstunden: {woche['ueberstunden']:.2f} Stunden\n\n"
        
        # Summen berechnen
        summen = {
            "arbeitszeit": sum(w['arbeitszeit'] for w in wochen_uebersichten),
            "pausezeit": sum(w['pausezeit'] for w in wochen_uebersichten),
            "gesamtzeit": sum(w['gesamtzeit'] for w in wochen_uebersichten),
            "ueberstunden": sum(w['ueberstunden'] for w in wochen_uebersichten)
        }
        
        nachricht += "Summen:\n"
        nachricht += f"Gesamte Arbeitszeit: {summen['arbeitszeit']:.2f} Stunden\n"
        nachricht += f"Gesamte Pausezeit: {summen['pausezeit']:.2f} Stunden\n"
        nachricht += f"Gesamte Zeit: {summen['gesamtzeit']:.2f} Stunden\n"
        nachricht += f"Gesamte Überstunden: {summen['ueberstunden']:.2f} Stunden"
        
        # Zeige Dialog
        self.vorname_input.window.info_dialog(
            'Monatsübersicht',
            nachricht
        )

    async def on_pdf_export_press(self, widget):
        """Exportiert die Monatsübersicht als PDF"""
        try:
            # Hole den aktuellen Monat und Jahr
            current_date = datetime.now()
            
            # Erstelle den Dateinamen
            filename = f"Arbeitszeiterfassung_{self.vorname_input.value}_{self.nachname_input.value}_{current_date.year}_{current_date.month:02d}.pdf"
            
            # Erstelle den Pfad im Dokumente-Ordner
            output_path = os.path.join(os.path.expanduser("~"), "Dokumente", "Stempel", "exports")
            os.makedirs(output_path, exist_ok=True)
            pdf_path = os.path.join(output_path, filename)
            
            # Erstelle die PDF
            from ..functions.pdf_export import create_monthly_pdf
            create_monthly_pdf(
                self.db_handler,
                self.vorname_input.value,
                self.nachname_input.value,
                current_date.year,
                current_date.month,
                pdf_path
            )
            
            # Zeige Erfolgsmeldung
            self.vorname_input.window.info_dialog(
                "PDF Export",
                f"Die PDF wurde erfolgreich erstellt und unter\n{pdf_path}\ngespeichert."
            )
            
        except Exception as e:
            # Zeige Fehlermeldung
            self.vorname_input.window.error_dialog(
                "Fehler beim PDF Export",
                f"Es ist ein Fehler aufgetreten: {str(e)}"
            )
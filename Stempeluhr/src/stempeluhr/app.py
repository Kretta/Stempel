import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from .components.stempeluhr_element import StempelUhrElement
from .databaselogic.db_handler import DatabaseHandler
import logging
import asyncio

# Setze das Logging-Level für asyncio auf ERROR
logging.getLogger('asyncio').setLevel(logging.ERROR)

class StempeluhrApp(toga.App):
    def startup(self):
        # Initialisiere den DatabaseHandler
        self.db_handler = DatabaseHandler()
        
        # Erstelle den Hauptcontainer
        main_box = toga.Box(
            style=Pack(
                direction=COLUMN
            )
        )

        # Erstelle die Stempeluhr-Komponente mit dem DatabaseHandler
        self.stempeluhr = StempelUhrElement("main", self.db_handler)
        main_box.add(self.stempeluhr.get_card())
        
        # Erstelle das Hauptfenster
        self.main_window = toga.MainWindow(
            title="Stempeluhr",
            size=(800, 600)
        )
        
        # Setze den Hauptcontainer als Fensterinhalt
        self.main_window.content = main_box
        self.main_window.show()

def main():
    return StempeluhrApp("Stempeluhr")


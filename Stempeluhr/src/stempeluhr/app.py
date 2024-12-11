import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from .components.stempeluhr_element import StempelUhrElement
import logging
import asyncio
# Setze das Logging-Level für asyncio auf ERROR
logging.getLogger('asyncio').setLevel(logging.ERROR)

class StempeluhrApp(toga.App):
    def startup(self):
        main_box = toga.Box(style=Pack(direction=COLUMN))
        self.stempeluhr = StempelUhrElement("main")
        main_box.add(self.stempeluhr.get_card())
        
        self.main_window = toga.MainWindow(title="Stempeluhr")
        self.main_window.content = main_box
        self.main_window.show()

def main():
    return StempeluhrApp("Stempeluhr")


import toga

def show_alert(window: toga.Window, title: str, message: str) -> None:
    """
    Zeigt eine einfache Informationsmeldung an.
    
    Args:
        window: Das Fenster, in dem die Meldung angezeigt werden soll
        title: Der Titel der Meldung
        message: Der Text der Meldung
    """
    window.info_dialog(title, message)
    
def show_confirmation(window: toga.Window, title: str, message: str) -> bool:
    """
    Zeigt eine Bestätigungsmeldung mit Ja/Nein-Option an.
    
    Args:
        window: Das Fenster, in dem die Meldung angezeigt werden soll
        title: Der Titel der Meldung
        message: Der Text der Meldung
        
    Returns:
        bool: True wenn der Benutzer "Ja" wählt, False sonst
    """
    return window.question_dialog(title, message)
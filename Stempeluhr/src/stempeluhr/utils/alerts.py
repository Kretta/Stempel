import toga

def show_alert(window: toga.Window, title: str, message: str) -> None:
    """
    Zeigt eine einfache Informationsmeldung an.
    """
    window.dialog(toga.InfoDialog(title=title, message=message))
    
def show_confirmation(window: toga.Window, title: str, message: str) -> bool:
    """
    Zeigt eine Bestätigungsmeldung mit Ja/Nein-Option an.
    """
    return window.dialog(toga.QuestionDialog(title=title, message=message))

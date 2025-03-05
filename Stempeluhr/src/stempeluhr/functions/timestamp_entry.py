from datetime import datetime

def create_timestamp_entry():
    # Aktuellen Zeitstempel erstellen
    current_time = datetime.now()
    
    # Zeitstempel im gewünschten Format formatieren
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Hier können weitere Daten zum Zeitstempel hinzugefügt werden
    entry = {
        "timestamp": timestamp,
        "type": "clock_in"  # oder "clock_out" je nach Bedarf
    }
    
    return entry

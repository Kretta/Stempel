from dataclasses import dataclass

@dataclass
class TimeEntry:
    vorname: str
    nachname: str
    date: str
    time: str
    status: str

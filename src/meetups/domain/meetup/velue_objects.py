from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Location:
    address: str
    city: str
    country: str


@dataclass(frozen=True)
class TimeSlot:
    start: date
    finish_date: date
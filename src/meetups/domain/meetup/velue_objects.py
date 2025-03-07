from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Location:
    address: str
    city: str
    country: str


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    finish_date: datetime

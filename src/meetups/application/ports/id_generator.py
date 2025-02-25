from abc import ABC, abstractmethod

from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.shared.event_id import EventId


class IdGenerator(ABC):
    @abstractmethod
    def generate_event_id(self) -> EventId: ...
    @abstractmethod
    def generate_meetup_id(self) -> MeetupId: ...

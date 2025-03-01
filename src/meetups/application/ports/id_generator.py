from abc import ABC, abstractmethod

from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.reviews.review_id import ReviewId
from meetups.domain.shared.event_id import EventId


class IdGenerator(ABC):
    @abstractmethod
    def generate_event_id(self) -> EventId: ...
    @abstractmethod
    def generate_meetup_id(self) -> MeetupId: ...
    @abstractmethod
    def generate_review_id(self) -> ReviewId: ...

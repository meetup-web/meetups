from abc import ABC, abstractmethod

from meetups.domain.meetup.velue_objects import Location, TimeSlot
from meetups.domain.meetup.meetup import Meetup
from meetups.domain.shared.user_id import UserId


class MeetupFactory(ABC):
    @abstractmethod
    def create(
        self, 
        title: str,
        desription: str,
        location: Location,
        time: TimeSlot,
        creator_id: UserId
    ) -> Meetup: ...
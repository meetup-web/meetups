from abc import ABC, abstractmethod

from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.meetup import Meetup


class MeetupRepository(ABC):
    @abstractmethod
    def add(self, meetup: Meetup) -> None: ...
    @abstractmethod
    def delete(self, meetup: Meetup) -> None: ...
    @abstractmethod
    async def load(self, meetup_id: MeetupId) -> Meetup | None: ...
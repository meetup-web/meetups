from abc import ABC, abstractmethod
from collections.abc import Iterable

from meetups.domain.meetup.meetup import Meetup
from meetups.domain.meetup.meetup_id import MeetupId


class MeetupRepository(ABC):
    @abstractmethod
    def add(self, meetup: Meetup) -> None: ...
    @abstractmethod
    def delete(self, meetup: Meetup) -> None: ...
    @abstractmethod
    async def load(self, meetup_id: MeetupId) -> Meetup | None: ...
    @abstractmethod
    async def load_all(self) -> Iterable[Meetup]: ...

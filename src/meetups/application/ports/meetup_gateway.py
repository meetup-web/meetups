from abc import ABC, abstractmethod
from collections.abc import Iterable

from meetups.application.models.meetup import MeetupReadModel
from meetups.application.models.pagination import Pagination


class MeetupGateway(ABC):
    @abstractmethod
    async def load_many(
        self,
        pagination: Pagination,
    ) -> Iterable[MeetupReadModel]: ...

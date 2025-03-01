from abc import ABC, abstractmethod
from collections.abc import Iterable

from meetups.application.models.pagination import Pagination
from meetups.application.models.review import ReviewReadModel
from meetups.domain.meetup.meetup_id import MeetupId


class ReviewGateway(ABC):
    @abstractmethod
    async def load(
        self, meetup_id: MeetupId, pagination: Pagination
    ) -> Iterable[ReviewReadModel]: ...

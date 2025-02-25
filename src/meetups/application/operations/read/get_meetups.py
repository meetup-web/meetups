from dataclasses import dataclass
from collections.abc import Iterable

from bazario.asyncio import RequestHandler

from meetups.application.common.markers.query import Query
from meetups.application.models.pagination import Pagination
from meetups.application.models.meetup import MeetupReadModel
from meetups.application.ports.meetup_gateway import MeetupGateway


@dataclass(frozen=True)
class GetMeetups(Query[Iterable[MeetupReadModel]]):
    pagination: Pagination


class GetMeetupsHandler(RequestHandler[GetMeetups, Iterable[MeetupReadModel]]):
    def __init__(self, meetup_gateway: MeetupGateway) -> None:
        self._meetup_gateway = meetup_gateway

    async def handle(self, request: GetMeetups) -> Iterable[MeetupReadModel]:
        meetups = await self._meetup_gateway.load_many(
            pagination=request.pagination
        )

        return meetups
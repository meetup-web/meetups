from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from meetups.application.common.application_error import (
    ApplicationError,
    ErrorType
)
from meetups.application.ports.time_provider import TimeProvider
from meetups.domain.meetup.events import MeetupDeleted
from meetups.application.common.markers.command import Command
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.repository import MeetupRepository


@dataclass(frozen=True)
class RemoveMeetup(Command[None]):
    meetup_id: MeetupId


class RemoveMeetupHandler(RequestHandler[RemoveMeetup, None]):
    def __init__(
        self, 
        meetup_repository: MeetupRepository,
        time_provider: TimeProvider
    ) -> None:
        self._meetup_repository = meetup_repository
        self._time_provider = time_provider

    async def handle(self, request: RemoveMeetup) -> None:
        meetup = await self._meetup_repository.load(request.meetup_id)

        if not meetup:
            raise ApplicationError(
                error_type=ErrorType.NOT_FOUND,
                message="Meetup not found"
            )
        
        event = MeetupDeleted(
            meetup_id=request.meetup_id,
            event_date=self._time_provider.provide_current()
        )
        meetup.add_event(event)
        
        self._meetup_repository.delete(meetup)
        




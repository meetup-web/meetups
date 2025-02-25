from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from meetups.application.common.application_error import (
    ApplicationError,
    ErrorType
)
from meetups.application.common.markers.command import Command
from meetups.application.ports.context.identity_provider import IdentityProvider
from meetups.application.ports.context.user_role import UserRole
from meetups.application.ports.time_provider import TimeProvider
from meetups.application.ports.id_generator import IdGenerator
from meetups.domain.meetup.factory import MeetupFactory
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.repository import MeetupRepository
from meetups.domain.meetup.velue_objects import Location, TimeSlot


@dataclass(frozen=True)
class AddMeetup(Command[MeetupId]):
    title: str
    description: str
    time: TimeSlot
    location: Location


class AddMeetupHandler(RequestHandler[AddMeetup, MeetupId]):
    def __init__(
        self,
        repository: MeetupRepository,
        identity_provider: IdentityProvider,
        time_provider: TimeProvider,
        id_generator: IdGenerator,
        factory: MeetupFactory
    ) -> None:
        self._repository = repository
        self._factory = factory
        self._identity_provider = identity_provider
        self._time_provider = time_provider
        self._id_generator = id_generator

    async def handle(self, request: AddMeetup) -> MeetupId:
        current_user_id = await self._identity_provider.current_user_id()
        current_user_role = await self._identity_provider.current_user_role()

        if current_user_role != UserRole.ADMIN:
            raise ApplicationError(
                message="Only admin can add meetups",
                error_type=ErrorType.PERMISSION_ERROR
            )
        
        meetup = self._factory.create(
            title=request.title,
            desription=request.description,
            location=request.location,
            time=request.time,
            creator_id=current_user_id,
        )

        self._repository.add(meetup)

        return meetup.entity_id


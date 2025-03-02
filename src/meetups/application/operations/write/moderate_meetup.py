from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from meetups.application.common.application_error import (
    ApplicationError,
    ErrorType,
)
from meetups.application.common.markers.command import Command
from meetups.application.ports.context.identity_provider import IdentityProvider
from meetups.application.ports.context.user_role import UserRole
from meetups.application.ports.time_provider import TimeProvider
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.repository import MeetupRepository
from meetups.domain.shared.moderation import ModerationStatus


@dataclass(frozen=True)
class ModerateMeetup(Command[None]):
    meetup_id: MeetupId
    status: ModerationStatus


class ModerateMeetupHandler(RequestHandler[ModerateMeetup, None]):
    def __init__(
        self,
        meetup_repository: MeetupRepository,
        identity_provider: IdentityProvider,
        time_provider: TimeProvider,
    ) -> None:
        self._meetup_repository = meetup_repository
        self._identity_provider = identity_provider
        self._time_provider = time_provider

    async def handle(self, request: ModerateMeetup) -> None:
        current_user_role = await self._identity_provider.current_user_role()

        if current_user_role is not UserRole.ADMIN:
            raise ApplicationError(
                error_type=ErrorType.PERMISSION_ERROR,
                message="Only admin can moderate meetups",
            )

        meetup = await self._meetup_repository.load(request.meetup_id)

        if not meetup:
            raise ApplicationError(
                error_type=ErrorType.NOT_FOUND, message="Meetup not found"
            )

        meetup.update_moderation_status(
            moderation_status=request.status,
            current_date=self._time_provider.provide_current(),
        )

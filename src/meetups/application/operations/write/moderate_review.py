from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from meetups.application.common.application_error import (
    ApplicationError,
    ErrorType,
)
from meetups.application.common.markers.command import Command
from meetups.application.ports.context.identity_provider import IdentityProvider
from meetups.application.ports.context.user_role import UserRole
from meetups.application.ports.id_generator import IdGenerator
from meetups.application.ports.time_provider import TimeProvider
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.repository import MeetupRepository
from meetups.domain.reviews.review_id import ReviewId
from meetups.domain.shared.moderation import ModerationStatus


@dataclass(frozen=True)
class ModerateReview(Command):
    meetup_id: MeetupId
    review_id: ReviewId
    status: ModerationStatus


class ModerateReviewHandler(RequestHandler[ModerateReview, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        meetup_repository: MeetupRepository,
        time_provider: TimeProvider,
        id_generator: IdGenerator,
    ) -> None:
        self._identity_provider = identity_provider
        self._meetup_repository = meetup_repository
        self._time_provider = time_provider
        self._id_generator = id_generator

    async def handle(self, request: ModerateReview) -> None:
        current_user_role = await self._identity_provider.current_user_role()

        if current_user_role != UserRole.ADMIN:
            raise ApplicationError(
                error_type=ErrorType.PERMISSION_ERROR,
                message="Only admin can moderate reviews",
            )

        meetup = await self._meetup_repository.load(request.meetup_id)

        if not meetup:
            raise ApplicationError(
                error_type=ErrorType.NOT_FOUND,
                message="Meetup not found",
            )

        meetup.update_review_moderation_status(
            review_id=request.review_id,
            moder_status=request.status,
            current_date=self._time_provider.provide_current(),
        )

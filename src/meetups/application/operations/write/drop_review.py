from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from meetups.application.common.application_error import (
    ApplicationError,
    ErrorType,
)
from meetups.application.common.markers.command import Command
from meetups.application.ports.context.identity_provider import IdentityProvider
from meetups.application.ports.time_provider import TimeProvider
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.repository import MeetupRepository
from meetups.domain.reviews.review_id import ReviewId


@dataclass(frozen=True)
class DropReview(Command[None]):
    meetup_id: MeetupId
    review_id: ReviewId


class DropReviewHandler(RequestHandler[DropReview, None]):
    def __init__(
        self,
        meetup_repository: MeetupRepository,
        identity_provider: IdentityProvider,
        time_provider: TimeProvider,
    ) -> None:
        self._meetup_repository = meetup_repository
        self._identity_provider = identity_provider
        self._time_provider = time_provider

    async def handle(self, request: DropReview) -> None:
        current_user_id = await self._identity_provider.current_user_id()

        meetup = await self._meetup_repository.load(request.meetup_id)

        if not meetup:
            raise ApplicationError(
                error_type=ErrorType.NOT_FOUND, message="Meetup not found"
            )

        meetup.drop_review(
            review_id=request.review_id,
            editor_id=current_user_id,
            current_date=self._time_provider.provide_current(),
        )

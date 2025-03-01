from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from meetups.application.common.application_error import (
    ApplicationError,
    ErrorType,
)
from meetups.application.common.markers.command import Command
from meetups.application.ports.context.identity_provider import IdentityProvider
from meetups.application.ports.id_generator import IdGenerator
from meetups.application.ports.time_provider import TimeProvider
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.repository import MeetupRepository
from meetups.domain.reviews.review_id import ReviewId


@dataclass(frozen=True)
class AddReview(Command[ReviewId]):
    meetup_id: MeetupId
    rating: int
    comment: str


class AddReviewHandler(RequestHandler[AddReview, ReviewId]):
    def __init__(
        self,
        repository: MeetupRepository,
        identity_provider: IdentityProvider,
        time_provider: TimeProvider,
        id_generator: IdGenerator,
    ) -> None:
        self._repository = repository
        self._identity_provider = identity_provider
        self._time_provider = time_provider
        self._id_generator = id_generator

    async def handle(self, request: AddReview) -> ReviewId:
        current_user_id = await self._identity_provider.current_user_id()

        meetup = await self._repository.load(request.meetup_id)

        if not meetup:
            raise ApplicationError(
                error_type=ErrorType.NOT_FOUND, message="Meetup not found"
            )

        review = meetup.add_review(
            review_id=self._id_generator.generate_review_id(),
            reviwer_id=current_user_id,
            rating=request.rating,
            comment=request.comment,
            current_date=self._time_provider.provide_current(),
        )

        return review.entity_id

from collections.abc import Iterable
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from meetups.application.common.markers.query import Query
from meetups.application.models.pagination import Pagination
from meetups.application.models.review import ReviewReadModel
from meetups.application.ports.review_gateway import ReviewGateway
from meetups.domain.meetup.meetup_id import MeetupId


@dataclass(frozen=True)
class GetReviews(Query[Iterable[ReviewReadModel]]):
    meetup_id: MeetupId
    pagination: Pagination


class GetReviewsHandler(RequestHandler[GetReviews, Iterable[ReviewReadModel]]):
    def __init__(self, review_gateway: ReviewGateway) -> None:
        self._review_gateway = review_gateway

    async def handle(self, request: GetReviews) -> Iterable[ReviewReadModel]:
        reviews = await self._review_gateway.load(
            meetup_id=request.meetup_id, pagination=request.pagination
        )

        return reviews

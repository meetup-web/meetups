from collections.abc import Iterable
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from meetups.application.common.markers.query import Query
from meetups.application.models.pagination import Pagination
from meetups.application.models.review import ReviewReadModel
from meetups.application.ports.context.identity_provider import IdentityProvider
from meetups.application.ports.context.user_role import UserRole
from meetups.application.ports.review_gateway import ReviewGateway
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.shared.moderation_status import ModerationStatus


@dataclass(frozen=True)
class GetReviews(Query[Iterable[ReviewReadModel]]):
    meetup_id: MeetupId
    pagination: Pagination


class GetReviewsHandler(RequestHandler[GetReviews, Iterable[ReviewReadModel]]):
    def __init__(
        self, review_gateway: ReviewGateway, identity_provider: IdentityProvider
    ) -> None:
        self._review_gateway = review_gateway
        self._identity_provider = identity_provider

    async def handle(self, request: GetReviews) -> Iterable[ReviewReadModel]:
        current_user_role = await self._identity_provider.current_user_role()

        reviews = await self._review_gateway.load(
            meetup_id=request.meetup_id, pagination=request.pagination
        )

        if current_user_role == UserRole.USER:
            return [
                preview
                for preview in reviews
                if preview.moderation_status == ModerationStatus.APPROVED
            ]

        return reviews

from collections.abc import Iterable

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncConnection

from meetups.application.models.pagination import Pagination
from meetups.application.models.review import ReviewReadModel
from meetups.application.ports.review_gateway import ReviewGateway
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.reviews.review_id import ReviewId
from meetups.infrastructure.persistence.sql_tables import REVIEWS_TABLE


class SqlReviewGateway(ReviewGateway):
    def __init__(self, connection: AsyncConnection) -> None:
        self._connection = connection
        self._identity_map: dict[ReviewId, ReviewReadModel] = {}

    async def load(
        self, meetup_id: MeetupId, pagination: Pagination
    ) -> Iterable[ReviewReadModel]:
        statement = (
            select(
                REVIEWS_TABLE.c.review_id.label("review_id"),
                REVIEWS_TABLE.c.user_id.label("reviewer_id"),
                REVIEWS_TABLE.c.meetup_id.label("meetup_id"),
                REVIEWS_TABLE.c.comment.label("comment"),
                REVIEWS_TABLE.c.rating.label("rating"),
                REVIEWS_TABLE.c.posted_at.label("posted_at"),
                REVIEWS_TABLE.c.moderation_status.label("moderation_status"),
            )
            .where(REVIEWS_TABLE.c.meetup_id == meetup_id)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        cursor_result = await self._connection.execute(statement)

        reviews: list[ReviewReadModel] = []
        for cursor_row in cursor_result:
            reviews.append(review := self._load(cursor_row))
            self._identity_map[review.review_id] = review

        return reviews

    def _load(self, cursor_row: Row) -> ReviewReadModel:
        review = ReviewReadModel(
            review_id=ReviewId(cursor_row.review_id),
            reviewer_id=cursor_row.reviewer_id,
            meetup_id=MeetupId(cursor_row.meetup_id),
            comment=cursor_row.comment,
            rating=cursor_row.rating,
            posted_at=cursor_row.posted_at,
            moderation_status=cursor_row.moderation_status,
        )

        return review

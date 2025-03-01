from collections.abc import Sequence
from typing import Final

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncConnection

from meetups.domain.meetup.meetup import Meetup
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.repository import MeetupRepository
from meetups.domain.meetup.velue_objects import Location, TimeSlot
from meetups.domain.reviews.review import Review
from meetups.domain.reviews.reviews_collection import Reviews
from meetups.domain.shared.events import DomainEventAdder
from meetups.domain.shared.unit_of_work import UnitOfWork
from meetups.infrastructure.persistence.sql_tables import (
    MEETUPS_TABLE,
    REVIEWS_TABLE,
)


class SqlMeetupRepository(MeetupRepository):
    def __init__(
        self,
        connection: AsyncConnection,
        unit_of_work: UnitOfWork,
        event_adder: DomainEventAdder,
    ) -> None:
        self._connection = connection
        self._unit_of_work = unit_of_work
        self._event_adder = event_adder
        self._identity_map: dict[MeetupId, Meetup] = {}

    def add(self, meetup: Meetup) -> None:
        self._unit_of_work.register_new(meetup)
        self._identity_map[meetup.entity_id] = meetup

    def delete(self, meetup: Meetup) -> None:
        self._unit_of_work.register_deleted(meetup)
        self._identity_map.pop(meetup.entity_id)

    async def load(self, meetup_id: MeetupId) -> Meetup | None:
        if meetup_id in self._identity_map:
            return self._identity_map[meetup_id]

        statement = (
            select(
                MEETUPS_TABLE.c.meetup_id.label("entity_id"),
                MEETUPS_TABLE.c.user_id.label("creator_id"),
                MEETUPS_TABLE.c.title.label("title"),
                MEETUPS_TABLE.c.description.label("description"),
                MEETUPS_TABLE.c.address.label("address"),
                MEETUPS_TABLE.c.city.label("city"),
                MEETUPS_TABLE.c.country.label("country"),
                MEETUPS_TABLE.c.start_date.label("start_date"),
                MEETUPS_TABLE.c.finish_date.label("finish_date"),
                MEETUPS_TABLE.c.status.label("status"),
                MEETUPS_TABLE.c.posted_at.label("posted_at"),
                MEETUPS_TABLE.c.rating.label("rating"),
                MEETUPS_TABLE.c.moderation_status.label(
                    "meetup_moderation_status"
                ),
                REVIEWS_TABLE.c.review_id.label("review_id"),
                REVIEWS_TABLE.c.user_id.label("reviewer_id"),
                REVIEWS_TABLE.c.rating.label("review_rating"),
                REVIEWS_TABLE.c.comment.label("review_comment"),
                REVIEWS_TABLE.c.posted_at.label("review_posted_at"),
                REVIEWS_TABLE.c.moderation_status.label(
                    "review_moderation_status"
                ),
            )
            .join(
                REVIEWS_TABLE,
                REVIEWS_TABLE.c.meetup_id == MEETUPS_TABLE.c.meetup_id,
                isouter=True,
            )
            .where(MEETUPS_TABLE.c.meetup_id == meetup_id)
        )
        cursor_result = await self._connection.execute(statement)
        cursor_rows = cursor_result.all()

        if not cursor_rows:
            return None

        return self._load(cursor_rows)

    def _load(self, cursor_res: Sequence[Row]) -> Meetup:
        reviews = Reviews()

        first_row: Final[Row] = cursor_res[0]

        meetup = Meetup(
            entity_id=MeetupId(first_row.entity_id),
            event_adder=self._event_adder,
            unit_of_work=self._unit_of_work,
            creator_id=first_row.creator_id,
            title=first_row.title,
            description=first_row.description,
            location=Location(
                address=first_row.address,
                city=first_row.city,
                country=first_row.country,
            ),
            time=TimeSlot(
                start=first_row.start_date,
                finish_date=first_row.finish_date,
            ),
            status=first_row.status,
            posted_at=first_row.posted_at,
            rating=first_row.rating,
            reviews=reviews,
            moderation_status=first_row.meetup_moderation_status,
        )

        for review_row in cursor_res:
            if review_row.review_id:
                review = Review(
                    meetup_id=meetup.entity_id,
                    entity_id=review_row.review_id,
                    unit_of_work=self._unit_of_work,
                    event_adder=self._event_adder,
                    reviewer_id=review_row.reviewer_id,
                    rating=review_row.review_rating,
                    comment=review_row.review_comment,
                    added_at=review_row.review_posted_at,
                    moderation_status=review_row.review_moderation_status,
                )
                reviews.add(review)

        return meetup

from sqlalchemy.ext.asyncio import AsyncConnection

from meetups.domain.reviews.review import Review
from meetups.infrastructure.persistence.data_mapper import DataMapper
from meetups.infrastructure.persistence.sql_tables import REVIEWS_TABLE


class SqlReviewDataMapper(DataMapper[Review]):
    def __init__(self, connection: AsyncConnection) -> None:
        self._connection = connection

    async def insert(self, entity: Review) -> None:
        statement = REVIEWS_TABLE.insert().values(
            review_id=entity.entity_id,
            meetup_id=entity.meetup_id,
            user_id=entity.reviewer_id,
            rating=entity.rating,
            comment=entity.comment,
            posted_at=entity.added_at,
        )

        await self._connection.execute(statement)

    async def update(self, entity: Review) -> None:
        statement = (
            REVIEWS_TABLE.update()
            .where(REVIEWS_TABLE.c.review_id == entity.entity_id)
            .values(
                rating=entity.rating,
                comment=entity.comment,
            )
        )

        await self._connection.execute(statement)

    async def delete(self, entity: Review) -> None:
        statement = REVIEWS_TABLE.delete().where(
            REVIEWS_TABLE.c.review_id == entity.entity_id
        )

        await self._connection.execute(statement)

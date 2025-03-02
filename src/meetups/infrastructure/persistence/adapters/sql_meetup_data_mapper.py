from sqlalchemy.ext.asyncio import AsyncConnection

from meetups.domain.meetup.meetup import Meetup
from meetups.infrastructure.persistence.data_mapper import DataMapper
from meetups.infrastructure.persistence.sql_tables import MEETUPS_TABLE


class SqlMeetupDataMapper(DataMapper[Meetup]):
    def __init__(self, connection: AsyncConnection) -> None:
        self._connection = connection

    async def insert(self, entity: Meetup) -> None:
        statement = MEETUPS_TABLE.insert().values(
            meetup_id=entity.entity_id,
            user_id=entity.creator_id,
            title=entity.title,
            description=entity.description,
            rating=entity.rating,
            address=entity.location.address,
            city=entity.location.city,
            country=entity.location.country,
            start_date=entity.time.start,
            finish_date=entity.time.finish_date,
            status=entity.status.value,
            posted_at=entity.posted_at,
            moderation_status=entity.moderation_status,
        )
        await self._connection.execute(statement)

    async def update(self, entity: Meetup) -> None:
        statement = (
            MEETUPS_TABLE.update()
            .where(MEETUPS_TABLE.c.meetup_id == entity.entity_id)
            .values(
                status=entity.status.value,
                rating=entity.rating,
                moderation_status=entity.moderation_status,
            )
        )
        await self._connection.execute(statement)

    async def delete(self, entity: Meetup) -> None:
        statement = MEETUPS_TABLE.delete().where(
            MEETUPS_TABLE.c.meetup_id == entity.entity_id
        )
        await self._connection.execute(statement)

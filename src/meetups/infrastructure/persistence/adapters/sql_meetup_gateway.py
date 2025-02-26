from collections.abc import Iterable

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncConnection

from meetups.application.models.meetup import MeetupReadModel
from meetups.application.models.pagination import Pagination
from meetups.application.ports.meetup_gateway import MeetupGateway
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.velue_objects import Location, TimeSlot
from meetups.infrastructure.persistence.sql_tables import MEETUPS_TABLE


class SqlMeetupGateway(MeetupGateway):
    def __init__(self, connection: AsyncConnection) -> None:
        self._connection = connection
        self._identity_map: dict[MeetupId, MeetupReadModel] = {}

    async def load_many(self, pagination: Pagination) -> Iterable[MeetupReadModel]:
        statement = (
            select(
                MEETUPS_TABLE.c.meetup_id.label("meetup_id"),
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
            )
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        cursor_result = await self._connection.execute(statement)

        meetups: list[MeetupReadModel] = []
        for cursor_row in cursor_result:
            meetups.append(meetup := self._load(cursor_row))
            self._identity_map[meetup.meetup_id] = meetup

        return meetups

    def _load(self, cursor_row: Row) -> MeetupReadModel:
        meetup = MeetupReadModel(
            meetup_id=MeetupId(cursor_row.meetup_id),
            creator_id=cursor_row.creator_id,
            title=cursor_row.title,
            description=cursor_row.description,
            location=Location(
                address=cursor_row.address,
                city=cursor_row.city,
                country=cursor_row.country,
            ),
            time=TimeSlot(
                start=cursor_row.start_date,
                finish_date=cursor_row.finish_date,
            ),
            status=cursor_row.status,
            posted_at=cursor_row.posted_at,
        )

        return meetup

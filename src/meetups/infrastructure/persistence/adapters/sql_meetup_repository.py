from collections.abc import Iterable

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncConnection

from meetups.domain.meetup.meetup import Meetup
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.repository import MeetupRepository
from meetups.domain.meetup.velue_objects import Location, TimeSlot
from meetups.domain.shared.events import DomainEventAdder
from meetups.domain.shared.unit_of_work import UnitOfWork
from meetups.infrastructure.persistence.sql_tables import MEETUPS_TABLE


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

        statement = select(
            MEETUPS_TABLE.c.meetup_id.label("entity_id"),
            MEETUPS_TABLE.c.user_id.label("creator_id"),
            MEETUPS_TABLE.c.title.label("status"),
            MEETUPS_TABLE.c.description.label("description"),
            MEETUPS_TABLE.c.address.label("address"),
            MEETUPS_TABLE.c.city.label("city"),
            MEETUPS_TABLE.c.country.label("country"),
            MEETUPS_TABLE.c.start_date.label("start_date"),
            MEETUPS_TABLE.c.finish_date.label("finish_date"),
            MEETUPS_TABLE.c.status.label("status"),
            MEETUPS_TABLE.c.posted_at.label("posted_at"),
        ).where(MEETUPS_TABLE.c.meetup_id == meetup_id)
        cursor_result = await self._connection.execute(statement)
        cursor_row = cursor_result.first()

        if cursor_row is None:
            return None

        return self._load(cursor_row)

    async def load_all(self) -> Iterable[Meetup]:
        statement = select(
            MEETUPS_TABLE.c.meetup_id.label("entity_id"),
            MEETUPS_TABLE.c.user_id.label("creator_id"),
            MEETUPS_TABLE.c.title.label("status"),
            MEETUPS_TABLE.c.description.label("description"),
            MEETUPS_TABLE.c.address.label("address"),
            MEETUPS_TABLE.c.city.label("city"),
            MEETUPS_TABLE.c.country.label("country"),
            MEETUPS_TABLE.c.start_date.label("start_date"),
            MEETUPS_TABLE.c.finish_date.label("finish_date"),
            MEETUPS_TABLE.c.status.label("status"),
            MEETUPS_TABLE.c.posted_at.label("posted_at"),
        )
        cursor_result = await self._connection.execute(statement)

        meetups: list[Meetup] = []
        for row in cursor_result:
            meetups.append(meetup := self._load(row))
            self._identity_map[meetup.entity_id] = meetup

        return meetups

    def _load(self, cursor_row: Row) -> Meetup:
        meetup = Meetup(
            entity_id=MeetupId(cursor_row.entity_id),
            event_adder=self._event_adder,
            unit_of_work=self._unit_of_work,
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

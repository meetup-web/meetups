from collections.abc import Iterable

from meetups.application.ports.id_generator import IdGenerator
from meetups.application.ports.time_provider import TimeProvider
from meetups.domain.meetup.events import MeetupDeleted
from meetups.domain.meetup.meetup import Meetup
from meetups.domain.meetup.meetup_status import MeetupStatus
from meetups.domain.meetup.repository import MeetupRepository
from meetups.infrastructure.tasks.date_provider import DateProvider


class DeleteMeetupProcessor:
    def __init__(
        self,
        meetup_repository: MeetupRepository,
        date_provider: DateProvider,
        id_generator: IdGenerator,
        time_provider: TimeProvider,
    ) -> None:
        self._meetup_repository = meetup_repository
        self._date_provider = date_provider
        self._id_generator = id_generator
        self._time_provider = time_provider

    async def execute(self) -> None:
        meetups = await self._meetup_repository.load_all()
        deleted_meetups = self._filter_meetups(meetups)

        for meetup in deleted_meetups:
            self._meetup_repository.delete(meetup)
            meetup.add_event(
                MeetupDeleted(
                    meetup_id=meetup.entity_id,
                    event_date=self._time_provider.provide_current(),
                )
            )

    def _filter_meetups(self, meetups: Iterable[Meetup]) -> Iterable[Meetup]:
        return [
            meetup
            for meetup in meetups
            if meetup.status == MeetupStatus.COMPLETED
            or meetup.time.finish_date < self._date_provider.provide_current()
        ]

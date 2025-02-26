from collections.abc import Iterable

from meetups.application.ports.time_provider import TimeProvider
from meetups.domain.meetup.meetup import Meetup
from meetups.domain.meetup.meetup_status import MeetupStatus
from meetups.domain.meetup.repository import MeetupRepository
from meetups.infrastructure.tasks.date_provider import DateProvider


class EditMeetupStatusProcessor:
    def __init__(
        self,
        meetup_repository: MeetupRepository,
        date_provider: DateProvider,
        time_provider: TimeProvider,
    ) -> None:
        self._meetup_repository = meetup_repository
        self._date_provider = date_provider
        self._time_provider = time_provider

    async def execute(self) -> None:
        meetups = await self._meetup_repository.load_all()

        for meetup in self._coming_meetups(meetups):
            meetup.edit_meetup_status(
                status=MeetupStatus.COMING,
                current_date=self._time_provider.provide_current(),
            )

        for meetup in self._ended_meetups(meetups):
            meetup.edit_meetup_status(
                status=MeetupStatus.COMPLETED,
                current_date=self._time_provider.provide_current(),
            )

        for meetup in self._ongoing_meetups(meetups):
            meetup.edit_meetup_status(
                status=MeetupStatus.STARTED,
                current_date=self._time_provider.provide_current(),
            )

    def _coming_meetups(self, meetups: Iterable[Meetup]) -> Iterable[Meetup]:
        return [
            meetup
            for meetup in meetups
            if meetup.status != MeetupStatus.COMING
            and meetup.time.start > self._date_provider.provide_current()
        ]

    def _ended_meetups(self, meetups: Iterable[Meetup]) -> Iterable[Meetup]:
        return [
            meetup
            for meetup in meetups
            if meetup.status != MeetupStatus.COMPLETED
            and meetup.time.finish_date < self._date_provider.provide_current()
        ]

    def _ongoing_meetups(self, meetups: Iterable[Meetup]) -> Iterable[Meetup]:
        return [
            meetup
            for meetup in meetups
            if meetup.status != MeetupStatus.STARTED
            and meetup.time.start
            <= self._date_provider.provide_current()
            <= meetup.time.finish_date
        ]

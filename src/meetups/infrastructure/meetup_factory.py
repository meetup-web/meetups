from meetups.application.ports.id_generator import IdGenerator
from meetups.application.ports.time_provider import TimeProvider
from meetups.domain.meetup.events import MeetupCreated
from meetups.domain.meetup.factory import MeetupFactory
from meetups.domain.meetup.meetup import Meetup
from meetups.domain.meetup.velue_objects import Location, TimeSlot
from meetups.domain.shared.events import DomainEventAdder
from meetups.domain.shared.unit_of_work import UnitOfWork
from meetups.domain.shared.user_id import UserId


class MeetupFactoryImpl(MeetupFactory):
    def __init__(
        self,
        id_generator: IdGenerator,
        time_provider: TimeProvider,
        event_adder: DomainEventAdder,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._id_generator = id_generator
        self._time_provider = time_provider
        self._event_adder = event_adder
        self._unit_of_work = unit_of_work

    def create(
        self,
        title: str,
        description: str,
        location: Location,
        time: TimeSlot,
        creator_id: UserId,
    ) -> Meetup:
        meetup = Meetup(
            entity_id=self._id_generator.generate_meetup_id(),
            event_adder=self._event_adder,
            unit_of_work=self._unit_of_work,
            creator_id=creator_id,
            title=title,
            description=description,
            location=location,
            time=time,
            posted_at=self._time_provider.provide_current(),
        )
        event = MeetupCreated(
            meetup_id=meetup.entity_id,
            creator=creator_id,
            time=time,
            location=location,
            title=title,
            description=description,
            event_date=meetup.posted_at,
        )

        meetup.add_event(event)

        return meetup

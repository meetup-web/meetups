from uuid_extensions import uuid7  # type: ignore

from meetups.application.ports.id_generator import IdGenerator
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.shared.event_id import EventId


class UUID7IdGenerator(IdGenerator):
    def generate_event_id(self) -> EventId:
        return EventId(uuid7())

    def generate_meetup_id(self) -> MeetupId:
        return MeetupId(uuid7())
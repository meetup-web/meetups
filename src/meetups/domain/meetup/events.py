from dataclasses import dataclass
from decimal import Decimal

from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.meetup_status import MeetupStatus
from meetups.domain.meetup.velue_objects import Location, TimeSlot
from meetups.domain.shared.events import DomainEvent
from meetups.domain.shared.moderation import ModerationStatus
from meetups.domain.shared.user_id import UserId


@dataclass(frozen=True)
class MeetupCreated(DomainEvent):
    meetup_id: MeetupId
    creator: UserId
    time: TimeSlot
    location: Location
    title: str
    description: str


@dataclass(frozen=True)
class MeetupStatusChanged(DomainEvent):
    meetup_id: MeetupId
    status: MeetupStatus


@dataclass(frozen=True)
class MeetupRatingChanged(DomainEvent):
    meetup_id: MeetupId
    rating: Decimal


@dataclass(frozen=True)
class MeetupModerationStatusChanged(DomainEvent):
    meetup_id: MeetupId
    status: ModerationStatus


@dataclass(frozen=True)
class MeetupDeleted(DomainEvent):
    meetup_id: MeetupId

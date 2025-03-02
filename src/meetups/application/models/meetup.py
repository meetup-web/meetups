from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.meetup_status import MeetupStatus
from meetups.domain.meetup.velue_objects import Location, TimeSlot
from meetups.domain.shared.moderation import ModerationStatus
from meetups.domain.shared.user_id import UserId


@dataclass(frozen=True)
class MeetupReadModel:
    meetup_id: MeetupId
    creator_id: UserId
    title: str
    description: str
    location: Location
    time: TimeSlot
    status: MeetupStatus
    posted_at: datetime
    rating: Decimal
    moderation_status: ModerationStatus

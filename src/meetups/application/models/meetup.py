from dataclasses import dataclass
from datetime import datetime

from meetups.domain.meetup.meetup_status import MeetupStatus
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.shared.user_id import UserId
from meetups.domain.meetup.velue_objects import Location, TimeSlot


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

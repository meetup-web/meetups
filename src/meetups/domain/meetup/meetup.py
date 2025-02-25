from datetime import datetime

from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.velue_objects import Location, TimeSlot
from meetups.domain.meetup.meetup_status import MeetupStatus
from meetups.domain.meetup.events import MeetupStatusChanged
from meetups.domain.shared.entity import Entity
from meetups.domain.shared.unit_of_work import UnitOfWork
from meetups.domain.shared.user_id import UserId
from meetups.domain.shared.events import DomainEventAdder


class Meetup(Entity[MeetupId]):
    def __init__(
        self,
        entity_id: MeetupId,
        event_adder: DomainEventAdder,
        unit_of_work: UnitOfWork,
        *,
        creator_id: UserId,
        title: str,
        description: str,
        location: Location,
        time: TimeSlot,
        status: MeetupStatus = MeetupStatus.COMING,
        posted_at: datetime,
    ) -> None:
        Entity.__init__(self, entity_id, event_adder, unit_of_work)

        self._creator_id = creator_id
        self._title = title
        self._description = description
        self._location = location
        self._time = time
        self._status = status
        self._posted_at = posted_at
    
    def edit_meetup_status(
        self, status: MeetupStatus, current_date: datetime
    ) -> None:
        self._status = status
        event = MeetupStatusChanged(
            meetup_id=self._entity_id,
            status=status,
            event_date=current_date
        )
        self.mark_dirty()
        self.add_event(event)
    
    @property
    def creator_id(self) -> UserId:
        return self._creator_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def location(self) -> Location:
        return self._location
    
    @property
    def time(self) -> TimeSlot:
        return self._time
    
    @property
    def status(self) -> MeetupStatus:
        return self._status
    
    @property
    def posted_at(self) -> datetime:
        return self._posted_at


            

from datetime import datetime
from decimal import Decimal
from statistics import mean

from meetups.domain.meetup.events import MeetupRatingChanged, MeetupStatusChanged
from meetups.domain.meetup.exceptions import MeetupModerationRequiredError
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.meetup.meetup_status import MeetupStatus
from meetups.domain.meetup.velue_objects import Location, TimeSlot
from meetups.domain.reviews.events import ReviewAdded, ReviewDeleted
from meetups.domain.reviews.review import Review
from meetups.domain.reviews.review_id import ReviewId
from meetups.domain.reviews.reviews_collection import Reviews
from meetups.domain.shared.entity import Entity
from meetups.domain.shared.events import DomainEventAdder
from meetups.domain.shared.moderation import ModerationStatus
from meetups.domain.shared.unit_of_work import UnitOfWork
from meetups.domain.shared.user_id import UserId


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
        moderation_status: ModerationStatus = ModerationStatus.PENDING,
        reviews: Reviews = Reviews(),
        posted_at: datetime,
        rating: Decimal = Decimal("0.0"),
    ) -> None:
        Entity.__init__(self, entity_id, event_adder, unit_of_work)

        self._creator_id = creator_id
        self._title = title
        self._description = description
        self._location = location
        self._time = time
        self._status = status
        self._posted_at = posted_at
        self._rating = rating
        self._reviews = reviews
        self._moderation_status = moderation_status

    def update_moderation_status(
        self, moderation_status: ModerationStatus, current_date: datetime
    ) -> None:
        if moderation_status == self._moderation_status:
            return

        self._moderation_status = moderation_status
        self.mark_dirty()

    def update_review_moderation_status(
        self,
        review_id: ReviewId,
        moder_status: ModerationStatus,
        current_date: datetime,
    ) -> None:
        review = self._reviews.load(review_id)

        if moder_status == review.moderation_status:
            return

        review.update_moderation_status(
            moderation_status=moder_status, current_date=current_date
        )
        review.mark_dirty()

        self._update_rating(current_date=current_date)

    def add_review(
        self,
        review_id: ReviewId,
        reviwer_id: UserId,
        rating: int,
        comment: str,
        current_date: datetime,
    ) -> Review:
        self._ensure_moderated()
        review = Review(
            entity_id=review_id,
            unit_of_work=self._unit_of_work,
            event_adder=self._event_adder,
            meetup_id=self._entity_id,
            reviewer_id=reviwer_id,
            rating=rating,
            comment=comment,
            added_at=current_date,
        )
        event = ReviewAdded(
            review_id=review_id,
            meetup_id=self._entity_id,
            reviewer_id=reviwer_id,
            rating=rating,
            comment=comment,
            event_date=current_date,
        )
        self._reviews.add(review)
        review.mark_new()
        self.add_event(event)

        return review

    def update_review(
        self,
        review_id: ReviewId,
        editor_id: UserId,
        rating: int,
        comment: str,
        current_date: datetime,
    ) -> None:
        review = self._reviews.load(review_id)
        review.ensure_owner(editor_id)
        review.edit_review(rating, comment, current_date)
        review.mark_dirty()
        self._update_rating(current_date=current_date)

    def drop_review(
        self, review_id: ReviewId, current_date: datetime, editor_id: UserId
    ) -> None:
        review = self._reviews.load(review_id)
        review.ensure_owner(editor_id)
        review.mark_deleted()
        event = ReviewDeleted(review_id=review_id, event_date=current_date)
        self.add_event(event)
        self._reviews.remove(review)
        self._update_rating(current_date=current_date)

    def edit_meetup_status(
        self, status: MeetupStatus, current_date: datetime
    ) -> None:
        self._ensure_moderated()
        self._status = status
        event = MeetupStatusChanged(
            meetup_id=self._entity_id, status=status, event_date=current_date
        )
        self.mark_dirty()
        self.add_event(event)

    def _calculate_meetup_rating(self) -> Decimal:
        review_ratings: list[Decimal] = [
            Decimal(review.rating)
            for review in self._reviews
            if review.moderation_status == ModerationStatus.APPROVED
        ]

        return mean(review_ratings)

    def _update_rating(self, current_date: datetime) -> None:
        self._rating = self._calculate_meetup_rating()
        event = MeetupRatingChanged(
            meetup_id=self._entity_id, rating=self._rating, event_date=current_date
        )
        self.add_event(event)
        self.mark_dirty()

    def _ensure_moderated(self) -> None:
        if self._moderation_status != ModerationStatus.APPROVED:
            raise MeetupModerationRequiredError

    @property
    def moderation_status(self) -> ModerationStatus:
        return self._moderation_status

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

    @property
    def reviews(self) -> set[Review]:
        return self._reviews

    @property
    def rating(self) -> Decimal:
        return self._rating

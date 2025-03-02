from datetime import datetime

from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.reviews.events import ReviewCommentChanged, ReviewRatingChanged
from meetups.domain.reviews.exceptions import (
    OnlyOwnerCanUpdateReviewError,
    ReviewModerationRequiredError,
)
from meetups.domain.reviews.review_id import ReviewId
from meetups.domain.shared.entity import Entity
from meetups.domain.shared.events import DomainEventAdder
from meetups.domain.shared.moderation import ModerationStatus
from meetups.domain.shared.unit_of_work import UnitOfWork
from meetups.domain.shared.user_id import UserId


class Review(Entity[ReviewId]):
    def __init__(
        self,
        entity_id: ReviewId,
        unit_of_work: UnitOfWork,
        event_adder: DomainEventAdder,
        *,
        meetup_id: MeetupId,
        reviewer_id: UserId,
        rating: int,
        comment: str,
        moderation_status: ModerationStatus = ModerationStatus.PENDING,
        added_at: datetime,
    ) -> None:
        Entity.__init__(self, entity_id, event_adder, unit_of_work)

        self._meetup_id = meetup_id
        self._moderation_status = moderation_status
        self._reviewer_id = reviewer_id
        self._rating = rating
        self._comment = comment
        self._added_at = added_at

    def edit_review(
        self,
        rating: int,
        comment: str,
        current_date: datetime,
    ) -> None:
        self._ensure_moderated()
        self.update_moderation_status(ModerationStatus.PENDING, current_date)
        self.edit_rating(rating, current_date)
        self.edit_comment(comment, current_date)

    def update_moderation_status(
        self, moderation_status: ModerationStatus, current_date: datetime
    ) -> None:
        if moderation_status == self._moderation_status:
            return

        self._moderation_status = moderation_status

    def edit_rating(self, rating: int, current_date: datetime) -> None:
        if rating == self._rating:
            return

        self._rating = rating
        event = ReviewRatingChanged(
            review_id=self._entity_id, rating=rating, event_date=current_date
        )
        self.add_event(event)

    def edit_comment(self, comment: str, current_date: datetime) -> None:
        if comment == self._comment:
            return

        self._comment = comment
        event = ReviewCommentChanged(
            review_id=self._entity_id, comment=comment, event_date=current_date
        )
        self.add_event(event)

    def ensure_owner(self, user_id: UserId) -> None:
        if self._reviewer_id != user_id:
            raise OnlyOwnerCanUpdateReviewError

    def _ensure_moderated(self) -> None:
        if self._moderation_status != ModerationStatus.APPROVED:
            raise ReviewModerationRequiredError

    @property
    def meetup_id(self) -> MeetupId:
        return self._meetup_id

    @property
    def reviewer_id(self) -> UserId:
        return self._reviewer_id

    @property
    def rating(self) -> int:
        return self._rating

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def added_at(self) -> datetime:
        return self._added_at

    @property
    def moderation_status(self) -> ModerationStatus:
        return self._moderation_status

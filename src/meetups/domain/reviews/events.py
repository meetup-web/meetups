from dataclasses import dataclass

from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.reviews.review_id import ReviewId
from meetups.domain.shared.events import DomainEvent
from meetups.domain.shared.user_id import UserId


@dataclass(frozen=True)
class ReviewAdded(DomainEvent):
    review_id: ReviewId
    reviewer_id: UserId
    meetup_id: MeetupId
    rating: int
    comment: str


@dataclass(frozen=True)
class ReviewRatingChanged(DomainEvent):
    review_id: ReviewId
    rating: int


@dataclass(frozen=True)
class ReviewCommentChanged(DomainEvent):
    review_id: ReviewId
    comment: str


@dataclass(frozen=True)
class ReviewDeleted(DomainEvent):
    review_id: ReviewId

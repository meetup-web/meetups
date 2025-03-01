from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.reviews.review_id import ReviewId
from meetups.domain.shared.moderation_status import ModerationStatus
from meetups.domain.shared.user_id import UserId


@dataclass(frozen=True)
class ReviewReadModel:
    review_id: ReviewId
    reviewer_id: UserId
    meetup_id: MeetupId
    comment: str
    rating: Decimal
    posted_at: datetime
    moderation_status: ModerationStatus

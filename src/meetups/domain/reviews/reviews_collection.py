from meetups.domain.reviews.exceptions import (
    ReviewAlreadyAddedError,
    ReviewDoesNotExistError,
)
from meetups.domain.reviews.review import Review
from meetups.domain.reviews.review_id import ReviewId


class Reviews(set[Review]):
    def __init__(self) -> None:
        set.__init__(self)

    def add(self, element: Review) -> None:
        for review in self:
            if review.reviewer_id == element.reviewer_id:
                raise ReviewAlreadyAddedError

        super().add(element)

    def load(self, review_id: ReviewId) -> Review:
        for review in self:
            if review.entity_id == review_id:
                return review

        raise ReviewDoesNotExistError

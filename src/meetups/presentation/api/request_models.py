from dataclasses import dataclass


@dataclass(frozen=True)
class EditReviewRequest:
    rating: int
    comment: str

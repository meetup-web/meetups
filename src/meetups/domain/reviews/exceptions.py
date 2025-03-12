from dataclasses import dataclass, field

from meetups.domain.shared.exceptions import DomainError


@dataclass(frozen=True)
class OnlyOwnerCanUpdateReviewError(DomainError):
    message: str = field(default="Only owner can update review")


@dataclass(frozen=True)
class ReviewAlreadyAddedError(DomainError):
    message: str = field(default="Review already added")


@dataclass(frozen=True)
class ReviewDoesNotExistError(DomainError):
    message: str = field(default="Review does not exist")

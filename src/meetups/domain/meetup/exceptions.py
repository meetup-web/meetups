from dataclasses import dataclass, field

from meetups.domain.shared.exceptions import DomainError


@dataclass(frozen=True)
class MeetupModerationRequiredError(DomainError):
    message: str = field(default="Moderation is required")


@dataclass(frozen=True)
class MeetupNotFinishedError(DomainError):
    message: str = field(default="Meetup is not finished")

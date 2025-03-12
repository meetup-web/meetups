from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from meetups.domain.shared.moderation import ModerationStatus


class ContentType(str, Enum):
    MEETUP = "meetup"


@dataclass(frozen=True)
class ContentRef:
    content_type: ContentType
    contnet_id: UUID


@dataclass(frozen=True)
class ModerationDecisionProvided:
    task_id: UUID
    decision: ModerationStatus
    content_ref: ContentRef

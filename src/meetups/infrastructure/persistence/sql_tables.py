from sqlalchemy import (
    DECIMAL,
    UUID,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    MetaData,
    Table,
    Text,
)

from meetups.domain.meetup.meetup_status import MeetupStatus
from meetups.domain.shared.moderation import ModerationStatus

METADATA = MetaData()

MEETUPS_TABLE = Table(
    "meetups",
    METADATA,
    Column("meetup_id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), nullable=False),
    Column("title", Text, nullable=False),
    Column("description", Text, nullable=False),
    Column("rating", DECIMAL, nullable=False),
    Column("address", Text, nullable=False),
    Column("city", Text, nullable=False),
    Column("country", Text, nullable=False),
    Column("start_date", Date, nullable=False),
    Column("finish_date", Date, nullable=False),
    Column("status", Enum(MeetupStatus), nullable=False),
    Column("moderation_status", Enum(ModerationStatus), nullable=False),
    Column("posted_at", DateTime(timezone=True), nullable=False),
)

REVIEWS_TABLE = Table(
    "reviews",
    METADATA,
    Column("review_id", UUID(as_uuid=True), primary_key=True),
    Column(
        "meetup_id",
        UUID(as_uuid=True),
        ForeignKey("meetups.meetup_id"),
        nullable=False,
    ),
    Column("moderation_status", Enum(ModerationStatus), nullable=False),
    Column("user_id", UUID(as_uuid=True), nullable=False),
    Column("rating", DECIMAL, nullable=False),
    Column("comment", Text, nullable=False),
    Column("posted_at", DateTime(timezone=True), nullable=False),
)

OUTBOX_TABLE = Table(
    "outbox",
    METADATA,
    Column("message_id", UUID, primary_key=True),
    Column("data", Text, nullable=False),
    Column("event_type", Text, nullable=False, default=False),
)

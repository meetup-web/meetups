from sqlalchemy import UUID, Column, Date, DateTime, Enum, MetaData, Table, Text

from meetups.domain.meetup.meetup_status import MeetupStatus

METADATA = MetaData()

MEETUPS_TABLE = Table(
    "meetups",
    METADATA,
    Column("meetup_id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), nullable=False),
    Column("title", Text, nullable=False),
    Column("description", Text, nullable=False),
    Column("address", Text, nullable=False),
    Column("city", Text, nullable=False),
    Column("country", Text, nullable=False),
    Column("start_date", Date, nullable=False),
    Column("finish_date", Date, nullable=False),
    Column("status", Enum(MeetupStatus), nullable=False),
    Column("posted_at", DateTime, nullable=False),
)

OUTBOX_TABLE = Table(
    "outbox",
    METADATA,
    Column("message_id", UUID, primary_key=True),
    Column("data", Text, nullable=False),
    Column("event_type", Text, nullable=False, default=False),
)

from datetime import UTC, date, datetime

from meetups.infrastructure.tasks.date_provider import DateProvider


class UtcDateProvider(DateProvider):
    def provide_current(self) -> date:
        return datetime.now(UTC).date()

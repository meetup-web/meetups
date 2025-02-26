from datetime import UTC, _Date, datetime

from meetups.infrastructure.tasks.date_provider import DateProvider


class UtcDateProvider(DateProvider):
    def provide_current(self) -> _Date:
        return datetime.now(UTC).date()

from dishka import FromDishka
from dishka.integrations.taskiq import inject

from meetups.infrastructure.tasks.edit_meetup_status_processor import (
    EditMeetupStatusProcessor,
)


@inject
async def edit_meetup_status_cron_task(
    processor: FromDishka[EditMeetupStatusProcessor],
) -> None:
    await processor.execute()

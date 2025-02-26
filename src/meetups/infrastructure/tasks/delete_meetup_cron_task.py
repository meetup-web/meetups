from dishka import FromDishka
from dishka.integrations.taskiq import inject

from meetups.infrastructure.tasks.delete_meetup_processor import (
    DeleteMeetupProcessor,
)


@inject
async def remove_meetup_cron_task(
    processor: FromDishka[DeleteMeetupProcessor],
) -> None:
    await processor.execute()

from datetime import date

from bazario.asyncio import Sender
from dishka.integrations.taskiq import inject, FromDishka

from meetups.application.operations.write.edit_meetup_status import EditMeetupStatus
from meetups.application.operations.write.remove_meetup import RemoveMeetup
from meetups.application.ports.meetup_gateway import MeetupGateway
from meetups.application.models.pagination import Pagination
from meetups.domain.meetup.meetup_status import MeetupStatus


@inject
async def remove_meetup_cron_task(
    sender: FromDishka[Sender],
    meetup_gateway: FromDishka[MeetupGateway],
) -> None:
    meetups = await meetup_gateway.load_many(
        pagination=Pagination()
    )

    for meetup in meetups:
        if (
            meetup.time.finish_date - date.today()
        ):
            await sender.send(
                RemoveMeetup(
                    meetup_id=meetup.meetup_id,
                )
            )


@inject
async def edit_meetup_status_cron_task(
    sender: FromDishka[Sender],
    meetup_gateway: FromDishka[MeetupGateway],
) -> None:
    meetups = await meetup_gateway.load_many(
        pagination=Pagination()
    )

    for meetup in meetups:
        if (
            meetup.time.finish_date < date.today() and
            meetup.time.start > date.today()
        ):
            await sender.send(
                EditMeetupStatus(
                    meetup_id=meetup.meetup_id,
                    status=MeetupStatus.STARTED,
                )
            )

        if (
            meetup.time.start < date.today()
        ):
            await sender.send(
                EditMeetupStatus(
                    meetup_id=meetup.meetup_id,
                    status=MeetupStatus.COMING,
                )
            )

        if (
            meetup.time.finish_date < date.today()
        ):
            await sender.send(
                EditMeetupStatus(
                    meetup_id=meetup.meetup_id,
                    status=MeetupStatus.COMPLETED,
                )
            )


    
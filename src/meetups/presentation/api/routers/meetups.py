from collections.abc import Iterable
from typing import Annotated

from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Depends
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from meetups.application.common.application_error import ApplicationError
from meetups.application.models.meetup import MeetupReadModel
from meetups.application.models.pagination import Pagination
from meetups.application.operations.read.get_meetups import GetMeetups
from meetups.application.operations.write.add_meetup import AddMeetup
from meetups.application.operations.write.moderate_meetup import ModerateMeetup
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.shared.moderation import ModerationStatus
from meetups.presentation.api.response_models import (
    ErrorResponse,
    SuccessResponse,
)

MEETUPS_ROUTER = APIRouter(prefix="/meetups", tags=["meetups"])


@MEETUPS_ROUTER.post(
    path="/",
    responses={HTTP_201_CREATED: {"model": SuccessResponse[MeetupId]}},
    status_code=HTTP_201_CREATED,
)
@inject
async def create_meetup(
    request: AddMeetup, *, sender: FromDishka[Sender]
) -> SuccessResponse[MeetupId]:
    meetup_id = await sender.send(request=request)
    return SuccessResponse(result=meetup_id, status=HTTP_201_CREATED)


@MEETUPS_ROUTER.get(
    path="/all",
    responses={
        HTTP_200_OK: {"model": SuccessResponse[Iterable[MeetupReadModel]]},
        HTTP_403_FORBIDDEN: {"model": ErrorResponse[ApplicationError]},
    },
    status_code=HTTP_200_OK,
)
@inject
async def get_meetups(
    pagination: Annotated[Pagination, Depends()], *, sender: FromDishka[Sender]
) -> SuccessResponse[Iterable[MeetupReadModel]]:
    meetups = await sender.send(request=GetMeetups(pagination=pagination))
    return SuccessResponse(result=meetups, status=HTTP_200_OK)


@MEETUPS_ROUTER.put(
    path="/{meetup_id}/moderate",
    responses={
        HTTP_200_OK: {"model": SuccessResponse[None]},
        HTTP_403_FORBIDDEN: {"model": ErrorResponse[ApplicationError]},
        HTTP_404_NOT_FOUND: {"model": ErrorResponse[ApplicationError]},
    },
    status_code=HTTP_200_OK,
)
@inject
async def moderate_meetup(
    meetup_id: MeetupId,
    status: Annotated[ModerationStatus, Body()],
    *,
    sender: FromDishka[Sender],
) -> SuccessResponse[None]:
    await sender.send(request=ModerateMeetup(meetup_id=meetup_id, status=status))
    return SuccessResponse(status=HTTP_200_OK)

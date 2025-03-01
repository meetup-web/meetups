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
    HTTP_409_CONFLICT,
)

from meetups.application.common.application_error import ApplicationError
from meetups.application.models.pagination import Pagination
from meetups.application.models.review import ReviewReadModel
from meetups.application.operations.read.get_reviews import GetReviews
from meetups.application.operations.write.add_review import AddReview
from meetups.application.operations.write.drop_review import DropReview
from meetups.application.operations.write.edit_review import EditReview
from meetups.domain.meetup.exceptions import MeetupModerationRequiredError
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.domain.reviews.exceptions import (
    OnlyOwnerCanUpdateReviewError,
    ReviewAlreadyAddedError,
    ReviewDoesNotExistError,
    ReviewModerationRequiredError,
)
from meetups.domain.reviews.review_id import ReviewId
from meetups.presentation.api.request_models import EditReviewRequest
from meetups.presentation.api.response_models import (
    ErrorResponse,
    SuccessResponse,
)

REVIEWS_ROUTER = APIRouter(prefix="/reviews", tags=["reviews"])


@REVIEWS_ROUTER.post(
    path="/",
    responses={
        HTTP_201_CREATED: {"model": SuccessResponse[ReviewId]},
        HTTP_409_CONFLICT: {"model": ErrorResponse[ReviewAlreadyAddedError]},
        HTTP_404_NOT_FOUND: {"model": ErrorResponse[ApplicationError]},
        HTTP_403_FORBIDDEN: {
            "model": ErrorResponse[MeetupModerationRequiredError]
        },
    },
    status_code=HTTP_201_CREATED,
)
@inject
async def add_review(
    request: AddReview, *, sender: FromDishka[Sender]
) -> SuccessResponse[ReviewId]:
    review_id = await sender.send(request)
    return SuccessResponse(result=review_id, status=HTTP_201_CREATED)


@REVIEWS_ROUTER.get(
    path="/{meetup_id}/reviews",
    responses={HTTP_200_OK: {"model": SuccessResponse[Iterable[ReviewReadModel]]}},
    status_code=HTTP_200_OK,
)
@inject
async def get_reviews(
    meetup_id: MeetupId,
    pagination: Annotated[Pagination, Depends()],
    *,
    sender: FromDishka[Sender],
) -> SuccessResponse[Iterable[ReviewReadModel]]:
    reviews = await sender.send(GetReviews(meetup_id, pagination))
    return SuccessResponse(result=reviews, status=HTTP_200_OK)


@REVIEWS_ROUTER.delete(
    path="/{meetup_id}/{review_id}",
    responses={
        HTTP_200_OK: {"model": SuccessResponse[None]},
        HTTP_403_FORBIDDEN: {
            "model": ErrorResponse[OnlyOwnerCanUpdateReviewError]
        },
        HTTP_404_NOT_FOUND: {
            "model": ErrorResponse[ReviewDoesNotExistError | ApplicationError]
        },
    },
    status_code=HTTP_200_OK,
)
@inject
async def drop_review(
    meetup_id: MeetupId, review_id: ReviewId, *, sender: FromDishka[Sender]
) -> SuccessResponse[None]:
    await sender.send(DropReview(meetup_id, review_id))
    return SuccessResponse(status=HTTP_200_OK)


@REVIEWS_ROUTER.put(
    path="/{meetup_id}/{review_id}",
    responses={
        HTTP_200_OK: {"model": SuccessResponse[None]},
        HTTP_403_FORBIDDEN: {
            "model": ErrorResponse[
                OnlyOwnerCanUpdateReviewError
                | ReviewModerationRequiredError
                | MeetupModerationRequiredError
            ]
        },
        HTTP_404_NOT_FOUND: {
            "model": ErrorResponse[ReviewDoesNotExistError | ApplicationError]
        },
    },
    status_code=HTTP_200_OK,
)
@inject
async def edit_review(
    review_id: ReviewId,
    meetup_id: MeetupId,
    content: Annotated[EditReviewRequest, Body()],
    *,
    sender: FromDishka[Sender],
) -> SuccessResponse[None]:
    await sender.send(
        EditReview(meetup_id, review_id, content.comment, content.rating)
    )
    return SuccessResponse(status=HTTP_200_OK)

from dataclasses import asdict

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from meetups.application.common.application_error import (
    ApplicationError,
    ErrorType,
)
from meetups.domain.meetup.exceptions import (
    MeetupModerationRequiredError,
    MeetupNotFinishedError,
)
from meetups.domain.reviews.exceptions import (
    OnlyOwnerCanUpdateReviewError,
    ReviewAlreadyAddedError,
    ReviewDoesNotExistError,
)
from meetups.domain.shared.exceptions import DomainError
from meetups.presentation.api.response_models import ErrorData, ErrorResponse

STATUS_MAP = {
    ErrorType.NOT_FOUND: HTTP_404_NOT_FOUND,
    ErrorType.VALIDATION_ERROR: HTTP_422_UNPROCESSABLE_ENTITY,
    ErrorType.APPLICATION_ERROR: HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorType.PERMISSION_ERROR: HTTP_403_FORBIDDEN,
    ReviewDoesNotExistError: HTTP_404_NOT_FOUND,
    ReviewAlreadyAddedError: HTTP_409_CONFLICT,
    OnlyOwnerCanUpdateReviewError: HTTP_403_FORBIDDEN,
    MeetupModerationRequiredError: HTTP_403_FORBIDDEN,
    MeetupNotFinishedError: HTTP_409_CONFLICT,
}


async def application_error_handler(_: Request, exception: ApplicationError) -> Response:
    error_data = ErrorData[None](exception.message)
    status_code = STATUS_MAP[exception.error_type]
    response_content = ErrorResponse(status_code, error_data)

    return JSONResponse(asdict(response_content), status_code)


async def domain_error_handler(_: Request, exception: DomainError) -> Response:
    error_data = ErrorData[None](exception.message)
    status_code = STATUS_MAP[type(exception)]
    response_content = ErrorResponse(status_code, error_data)

    return JSONResponse(asdict(response_content), status_code)

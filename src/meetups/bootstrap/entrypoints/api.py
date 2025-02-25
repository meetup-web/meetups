from typing import cast

from dishka.integrations.fastapi import (
    setup_dishka as add_container_to_fastapi,
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import HTTPExceptionHandler

from meetups.application.common.application_error import ApplicationError
from meetups.bootstrap.config import get_database_config, get_rabbitmq_config
from meetups.bootstrap.container import bootstrap_api_container
from meetups.presentation.api.exception_handlers import application_error_handler
from meetups.presentation.api.routers.meetups import MEETUPS_ROUTER
from meetups.presentation.api.routers.healthcheck import HEALTHCHECK_ROUTER


def add_middlewares(application: FastAPI) -> None:
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )


def add_api_routers(application: FastAPI) -> None:
    application.include_router(HEALTHCHECK_ROUTER)
    application.include_router(MEETUPS_ROUTER)


def add_exception_handlers(application: FastAPI) -> None:
    application.add_exception_handler(
        ApplicationError,
        cast(HTTPExceptionHandler, application_error_handler),
    )


def bootstrap_application() -> FastAPI:
    application = FastAPI()
    dishka_container = bootstrap_api_container(
        get_rabbitmq_config(),
        get_database_config(),
    )

    add_middlewares(application)
    add_api_routers(application)
    add_exception_handlers(application)
    add_container_to_fastapi(dishka_container, application)

    return application

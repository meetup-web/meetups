from alembic.config import Config as AlembicConfig
from dishka import Container, AsyncContainer
from dishka import make_container, make_async_container
from uvicorn import Config as UvicornConfig
from uvicorn import Server as UvicornServer
from faststream.rabbit import RabbitBroker

from meetups.bootstrap.config import DatabaseConfig, RabbitmqConfig


def bootstrap_cli_container(
    alembic_config: AlembicConfig,
    uvicorn_config: UvicornConfig,
    uvicorn_server: UvicornServer,
) -> Container:
    return make_container()


def bootstrap_api_container(
    rabbitmq_config: RabbitmqConfig,
    database_config: DatabaseConfig,
) -> AsyncContainer:
    return make_async_container()


def bootstrap_worker_container(
    rabbitmq_config: RabbitmqConfig,
    database_config: DatabaseConfig,
    faststream_rabbit_broker: RabbitBroker,
) -> AsyncContainer: 
    return make_async_container()
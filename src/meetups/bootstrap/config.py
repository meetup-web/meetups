from dataclasses import dataclass
from importlib.resources import files
from os import environ

from alembic.config import Config as AlembicConfig
from uvicorn import Config as UvicornConfig

DEFAULT_DB_URI = "sqlite+aiosqlite:///blog.db"
DEFAULT_MQ_URI = "amqp://guest:guest@localhost:5672/"
DEFAULT_SERVER_HOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 8000


@dataclass(frozen=True)
class RabbitmqConfig:
    uri: str


@dataclass(frozen=True)
class DatabaseConfig:
    uri: str


def get_rabbitmq_config() -> RabbitmqConfig:
    return RabbitmqConfig(environ.get("RABBITMQ_URI", DEFAULT_MQ_URI))


def get_database_config() -> DatabaseConfig:
    return DatabaseConfig(environ.get("DATABASE_URI", DEFAULT_DB_URI))


def get_alembic_config() -> AlembicConfig:
    resource = files("blog.infrastructure.persistence.alembic")
    config_file = resource.joinpath("alembic.ini")
    config_object = AlembicConfig(str(config_file))
    config_object.set_main_option("sqlalchemy.url", get_database_config().uri)
    return config_object


def get_uvicorn_config() -> UvicornConfig:
    return UvicornConfig(
        environ.get(
            "SERVER_FACTORY_PATH",
            "blog.bootstrap.entrypoints.api:bootstrap_application",
        ),
        environ.get("SERVER_HOST", DEFAULT_SERVER_HOST),
        int(environ.get("SERVER_PORT", DEFAULT_SERVER_PORT)),
        factory=True,
    )

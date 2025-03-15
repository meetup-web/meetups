from dishka.integrations.faststream import (
    setup_dishka as add_container_to_faststream,
)
from faststream import FastStream
from faststream.rabbit.broker import RabbitBroker

from meetups.bootstrap.config import get_database_config, get_rabbitmq_config
from meetups.bootstrap.container import (
    bootstrap_api_container as bootstrap_stream_container,
)


def add_middlewares(broker: RabbitBroker) -> None:
    pass


def add_consumers(broker: RabbitBroker) -> None:
    pass


def bootstrap_stream() -> FastStream:
    rabbit_config = get_rabbitmq_config()
    broker = RabbitBroker(rabbit_config.uri)

    add_middlewares(broker=broker)
    add_consumers(broker=broker)

    application = FastStream(broker=broker)
    container = bootstrap_stream_container(
        rabbitmq_config=rabbit_config,
        database_config=get_database_config(),
    )
    add_container_to_faststream(container=container, app=application)

    return application

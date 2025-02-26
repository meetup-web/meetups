from enum import StrEnum
from typing import Final

from aio_pika import DeliveryMode, Message
from faststream.rabbit import RabbitBroker

from meetups.infrastructure.outbox.outbox_message import OutboxMessage
from meetups.infrastructure.outbox.outbox_publisher import OutboxPublisher
from meetups.infrastructure.outbox.outbox_serialization import to_json


class QueueName(StrEnum):
    MEETUPS = "meetups_queue"


class ExchangeName(StrEnum):
    MEETUPS = "meetups_exchange"


class RabbitmqOutboxPublisher(OutboxPublisher):
    _CONTENT_TYPE: Final[str] = "application/json"

    def __init__(self, broker: RabbitBroker) -> None:
        self._broker = broker

    async def publish(self, message: OutboxMessage) -> None:
        rabbit_message = self._build_rabbitmq_message(message)
        await self._broker.publish(
            rabbit_message,
            queue=QueueName.MEETUPS,
            exchange=ExchangeName.MEETUPS,
            routing_key=message.event_type,
        )

    def _build_rabbitmq_message(self, message: OutboxMessage) -> Message:
        return Message(
            body=to_json(message).encode(),
            content_type=self._CONTENT_TYPE,
            message_id=message.message_id.hex,
            delivery_mode=DeliveryMode.PERSISTENT,
        )

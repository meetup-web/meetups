from enum import StrEnum

from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream.rabbit import ExchangeType, RabbitExchange, RabbitQueue
from faststream.rabbit.router import RabbitRouter

from meetups.application.operations.write.moderate_meetup import ModerateMeetup
from meetups.domain.meetup.meetup_id import MeetupId
from meetups.presentation.stream.request_models import (
    ContentType,
    ModerationDecisionProvided,
)


class ExchangeName(StrEnum):
    MODERATION = "moderation_exchange"


MODERATION_ROUTER = RabbitRouter()


@MODERATION_ROUTER.subscriber(
    queue=RabbitQueue(
        name="moderated_content", durable=True, routing_key="ModerationDecisionAdded"
    ),
    exchange=RabbitExchange(
        name=ExchangeName.MODERATION, type=ExchangeType.DIRECT, durable=True
    ),
)
@inject
async def moderate_content(
    message: ModerationDecisionProvided,
    *,
    sender: FromDishka[Sender],
) -> None:
    match message.content_ref.content_type:
        case ContentType.MEETUP:
            await sender.send(
                ModerateMeetup(
                    meetup_id=MeetupId(message.content_ref.contnet_id),
                    status=message.decision,
                )
            )

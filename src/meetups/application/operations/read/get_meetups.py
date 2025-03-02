from collections.abc import Iterable
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from meetups.application.common.markers.query import Query
from meetups.application.models.meetup import MeetupReadModel
from meetups.application.models.pagination import Pagination
from meetups.application.ports.context.identity_provider import IdentityProvider
from meetups.application.ports.context.user_role import UserRole
from meetups.application.ports.meetup_gateway import MeetupGateway
from meetups.domain.shared.moderation import ModerationStatus


@dataclass(frozen=True)
class GetMeetups(Query[Iterable[MeetupReadModel]]):
    pagination: Pagination


class GetMeetupsHandler(RequestHandler[GetMeetups, Iterable[MeetupReadModel]]):
    def __init__(
        self, meetup_gateway: MeetupGateway, identity_provider: IdentityProvider
    ) -> None:
        self._meetup_gateway = meetup_gateway
        self._identity_provider = identity_provider

    async def handle(self, request: GetMeetups) -> Iterable[MeetupReadModel]:
        current_user_role = await self._identity_provider.current_user_role()

        meetups = await self._meetup_gateway.load_many(
            pagination=request.pagination
        )

        if current_user_role == UserRole.USER:
            return [
                meetup
                for meetup in meetups
                if meetup.moderation_status == ModerationStatus.APPROVED
            ]

        return meetups

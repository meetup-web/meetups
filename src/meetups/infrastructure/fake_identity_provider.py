from uuid_extensions import uuid7  # type: ignore

from meetups.application.ports.context.identity_provider import IdentityProvider
from meetups.application.ports.context.user_role import UserRole
from meetups.domain.shared.user_id import UserId


class FakeIdentityProvider(IdentityProvider):
    async def current_user_id(self) -> UserId:
        return UserId(uuid7())

    async def current_user_role(self) -> UserRole:
        return UserRole.ADMIN

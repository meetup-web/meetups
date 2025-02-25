from abc import ABC, abstractmethod

from meetups.application.ports.context.user_role import UserRole
from meetups.domain.shared.user_id import UserId


class IdentityProvider(ABC):
    @abstractmethod
    async def current_user_id(self) -> UserId: ...
    @abstractmethod
    async def current_user_role(self) -> UserRole: ...
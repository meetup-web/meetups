from bazario.asyncio import HandleNext, PipelineBehavior

from meetups.application.common.application_error import (
    ApplicationError,
    ErrorType,
)
from meetups.application.operations.write.add_meetup import AddMeetup
from meetups.application.ports.context.identity_provider import IdentityProvider
from meetups.application.ports.context.user_role import UserRole


class ValidateUserRoleBehavior(PipelineBehavior[AddMeetup, None]):
    def __init__(self, identity_provider: IdentityProvider) -> None:
        self._identity_provider = identity_provider

    async def handle(
        self,
        request: AddMeetup,
        handle_next: HandleNext[AddMeetup, None],
    ) -> None:
        current_user_role = await self._identity_provider.current_user_role()

        if current_user_role != UserRole.ADMIN:
            raise ApplicationError(
                error_type=ErrorType.PERMISSION_ERROR,
                message="You are not allowed to add a meetup",
            )

        return await handle_next(request)

from collections.abc import AsyncIterator

from alembic.config import Config as AlembicConfig
from bazario.asyncio import Dispatcher, Registry
from bazario.asyncio.resolvers.dishka import DishkaResolver
from dishka import (
    Provider,
    Scope,
    WithParents,
    alias,
    from_context,
    provide,
    provide_all,
)
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    create_async_engine,
)
from uvicorn import Config as UvicornConfig
from uvicorn import Server as UvicornServer

from meetups.application.common.behaviors.commition_behavior import (
    CommitionBehavior,
)
from meetups.application.common.behaviors.event_id_generation_behavior import (
    EventIdGenerationBehavior,
)
from meetups.application.common.behaviors.event_publishing_behavior import (
    EventPublishingBehavior,
)
from meetups.application.common.markers.command import Command
from meetups.application.operations.behaviors.validate_user_role_behavior import (
    ValidateUserRoleBehavior,
)
from meetups.application.operations.read.get_meetups import (
    GetMeetups,
    GetMeetupsHandler,
)
from meetups.application.operations.write.add_meetup import (
    AddMeetup,
    AddMeetupHandler,
)
from meetups.bootstrap.config import (
    DatabaseConfig,
    RabbitmqConfig,
)
from meetups.domain.shared.events import DomainEvent
from meetups.infrastructure.domain_events import DomainEvents
from meetups.infrastructure.meetup_factory import MeetupFactoryImpl
from meetups.infrastructure.outbox.adapters.rabbitmq_outbox_publisher import (
    RabbitmqOutboxPublisher,
)
from meetups.infrastructure.outbox.outbox_processor import OutboxProcessor
from meetups.infrastructure.outbox.outbox_publisher import OutboxPublisher
from meetups.infrastructure.outbox.outbox_storing_handler import (
    OutboxStoringHandler,
)
from meetups.infrastructure.persistence.adapters.sql_data_mappers_registry import (
    SqlDataMappersRegistry,
)
from meetups.infrastructure.persistence.adapters.sql_meetup_data_mapper import (
    SqlMeetupDataMapper,
)
from meetups.infrastructure.persistence.adapters.sql_meetup_gateway import (
    SqlMeetupGateway,
)
from meetups.infrastructure.persistence.adapters.sql_meetup_repository import (
    SqlMeetupRepository,
)
from meetups.infrastructure.persistence.adapters.sql_outbox_gateway import (
    SqlOutboxGateway,
)
from meetups.infrastructure.persistence.adapters.unit_of_work import (
    UnitOfWorkImpl,
)
from meetups.infrastructure.persistence.transaction import Transaction
from meetups.infrastructure.tasks.adapters.uts_date_provider import (
    UtcDateProvider,
)
from meetups.infrastructure.tasks.delete_meetup_processor import (
    DeleteMeetupProcessor,
)
from meetups.infrastructure.tasks.edit_meetup_status_processor import (
    EditMeetupStatusProcessor,
)
from meetups.infrastructure.utc_time_provider import UtcTimeProvider
from meetups.infrastructure.uuid7_id_generator import UUID7IdGenerator


class ApiConfigProvider(Provider):
    scope = Scope.APP

    rabbitmq_config = from_context(RabbitmqConfig)
    database_config = from_context(DatabaseConfig)


class PersistenceProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def engine(
        self, postgres_config: DatabaseConfig
    ) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(postgres_config.uri)
        yield engine
        await engine.dispose()

    @provide
    async def connection(
        self, engine: AsyncEngine
    ) -> AsyncIterator[AsyncConnection]:
        async with engine.connect() as connection:
            yield connection


class DomainAdaptersProvider(Provider):
    scope = Scope.REQUEST

    repositories = provide_all(
        WithParents[SqlMeetupRepository]  # type: ignore[misc]
    )
    domain_events = provide(WithParents[DomainEvents])  # type: ignore[misc]
    meetup_factory = provide(WithParents[MeetupFactoryImpl])  # type: ignore[misc]
    unit_of_work = provide(WithParents[UnitOfWorkImpl])  # type: ignore[misc]


class ApplicationAdaptersProvider(Provider):
    scope = Scope.REQUEST

    gateways = provide_all(
        WithParents[SqlMeetupGateway],  # type: ignore[misc]
        WithParents[SqlOutboxGateway],  # type: ignore[misc]
    )
    id_generator = provide(
        WithParents[UUID7IdGenerator],  # type: ignore[misc]
        scope=Scope.APP,
    )
    time_provider = provide(
        WithParents[UtcTimeProvider],  # type: ignore[misc]
        scope=Scope.APP,
    )
    date_provider = provide(
        WithParents[UtcDateProvider],  # type: ignore[misc]
        scope=Scope.APP,
    )


class InfrastructureAdaptersProvider(Provider):
    scope = Scope.REQUEST

    transaction = alias(AsyncConnection, provides=Transaction)
    data_mappers = provide_all(
        WithParents[SqlMeetupDataMapper],  # type: ignore[misc]
    )
    data_mappers_registry = provide(
        WithParents[SqlDataMappersRegistry],  # type: ignore[misc]
    )


class ApplicationHandlersProvider(Provider):
    scope = Scope.REQUEST

    hanlers = provide_all(AddMeetupHandler, GetMeetupsHandler)
    behaviors = provide_all(
        CommitionBehavior,
        EventPublishingBehavior,
        EventIdGenerationBehavior,
        ValidateUserRoleBehavior,
    )


class BazarioProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def registry(self) -> Registry:
        registry = Registry()

        registry.add_request_handler(AddMeetup, AddMeetupHandler)
        registry.add_request_handler(GetMeetups, GetMeetupsHandler)
        registry.add_notification_handlers(DomainEvent, OutboxStoringHandler)
        registry.add_pipeline_behaviors(DomainEvent, EventIdGenerationBehavior)
        registry.add_pipeline_behaviors(AddMeetup, ValidateUserRoleBehavior)
        registry.add_pipeline_behaviors(
            Command,
            EventPublishingBehavior,
            CommitionBehavior,
        )

        return registry

    resolver = provide(WithParents[DishkaResolver])  # type: ignore[misc]
    dispatcher = provide(WithParents[Dispatcher])  # type: ignore[misc]


class CliConfigProvider(Provider):
    scope = Scope.APP

    alembic_config = from_context(AlembicConfig)
    uvicorn_config = from_context(UvicornConfig)
    uvicorn_server = from_context(UvicornServer)


class BrokerProvider(Provider):
    scope = Scope.APP

    faststream_rabbit_broker = from_context(RabbitBroker)


class OutboxProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def outbox_publisher(
        self,
        broker: RabbitBroker,
    ) -> OutboxPublisher:
        return RabbitmqOutboxPublisher(broker=broker)

    @provide
    async def outbox_processor(
        self,
        transaction: Transaction,
        outbox_gateway: SqlOutboxGateway,
        outbox_publisher: RabbitmqOutboxPublisher,
    ) -> OutboxProcessor:
        return OutboxProcessor(
            transaction=transaction,
            outbox_gateway=outbox_gateway,
            outbox_publisher=outbox_publisher,
        )


class TasksProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def delete_meetup_processor(
        self,
        repository: SqlMeetupRepository,
        date_provider: UtcDateProvider,
        time_provider: UtcTimeProvider,
        ig_generator: UUID7IdGenerator,
    ) -> DeleteMeetupProcessor:
        return DeleteMeetupProcessor(
            meetup_repository=repository,
            date_provider=date_provider,
            id_generator=ig_generator,
            time_provider=time_provider,
        )

    @provide
    async def edit_meetup_status_processor(
        self,
        repository: SqlMeetupRepository,
        date_provider: UtcDateProvider,
        time_provider: UtcTimeProvider,
    ) -> EditMeetupStatusProcessor:
        return EditMeetupStatusProcessor(
            meetup_repository=repository,
            date_provider=date_provider,
            time_provider=time_provider,
        )

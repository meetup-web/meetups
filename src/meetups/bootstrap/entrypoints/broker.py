from dishka.integrations.taskiq import (
    setup_dishka as add_container_to_taskiq,
)
from faststream.rabbit import RabbitBroker
from taskiq import TaskiqEvents, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker

from meetups.bootstrap.config import get_database_config, get_rabbitmq_config
from meetups.bootstrap.container import bootstrap_worker_container
from meetups.infrastructure.outbox.process_outbox_cron_task import (
    process_outbox,
)
from meetups.infrastructure.tasks.delete_meetup_cron_task import (
    remove_meetup_cron_task,
)
from meetups.infrastructure.tasks.edit_meetup_status_cron_task import (
    edit_meetup_status_cron_task,
)


def add_tasks_to_taskiq(broker: AioPikaBroker) -> None:
    broker.register_task(
        process_outbox, "process_outbox", schedule=[{"cron": "*/3 * * * *"}]
    )
    broker.register_task(
        remove_meetup_cron_task,
        "remove_meetup",
        schedule=[{"cron": "*/3 * * * *"}],
    )
    broker.register_task(
        edit_meetup_status_cron_task,
        "edit_meetup_status",
        schedule=[{"cron": "*/3 * * * *"}],
    )


def add_event_handlers(broker: AioPikaBroker) -> None:
    broker.add_event_handler(
        TaskiqEvents.WORKER_STARTUP,
        broker.state.faststream_broker.start,
    )


def bootstrap_broker() -> AioPikaBroker:
    rabbitmq_config = get_rabbitmq_config()
    database_config = get_database_config()
    taskiq_broker = AioPikaBroker(
        rabbitmq_config.uri,
        taskiq_return_missed_task=True,
        prefetch_count=1,
    )
    faststream_rabbitmq_broker = RabbitBroker(rabbitmq_config.uri)
    taskiq_broker.state.faststream_broker = faststream_rabbitmq_broker
    container = bootstrap_worker_container(
        rabbitmq_config,
        database_config,
        faststream_rabbitmq_broker,
    )

    add_tasks_to_taskiq(taskiq_broker)
    add_event_handlers(taskiq_broker)
    add_container_to_taskiq(container, taskiq_broker)

    return taskiq_broker


def bootstrap_sheduler() -> TaskiqScheduler:
    taskiq_broker = bootstrap_broker()
    sheduler = TaskiqScheduler(
        broker=taskiq_broker,
        sources=[
            LabelScheduleSource(taskiq_broker),
        ],
    )

    return sheduler

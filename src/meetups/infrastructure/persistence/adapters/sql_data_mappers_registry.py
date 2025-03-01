from meetups.domain.meetup.meetup import Meetup
from meetups.domain.reviews.review import Review
from meetups.domain.shared.entity import Entity
from meetups.infrastructure.persistence.adapters.sql_meetup_data_mapper import (
    SqlMeetupDataMapper,
)
from meetups.infrastructure.persistence.adapters.sql_review_data_mapper import (
    SqlReviewDataMapper,
)
from meetups.infrastructure.persistence.data_mapper import DataMapper
from meetups.infrastructure.persistence.data_mappers_registry import (
    DataMappersRegistry,
)


class SqlDataMappersRegistry(DataMappersRegistry):
    def __init__(
        self,
        meetup_data_mapper: SqlMeetupDataMapper,
        review_data_mapper: SqlReviewDataMapper,
    ) -> None:
        self._data_mappers_map: dict[type[Entity], DataMapper] = {
            Meetup: meetup_data_mapper,
            Review: review_data_mapper,
        }

    def get_mapper[EntityT: Entity](
        self, entity: type[EntityT]
    ) -> DataMapper[EntityT]:
        mapper = self._data_mappers_map.get(entity)

        if not mapper:
            raise KeyError(f"DataMapper for {entity.__name__!r} not registered")

        return mapper

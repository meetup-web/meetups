from abc import ABC, abstractmethod

from meetups.domain.shared.entity import Entity
from meetups.infrastructure.persistence.data_mapper import DataMapper


class DataMappersRegistry(ABC):
    @abstractmethod
    def get_mapper(self, entity: type[Entity]) -> DataMapper: ...

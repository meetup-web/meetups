from abc import ABC, abstractmethod
from datetime import date


class DateProvider(ABC):
    @abstractmethod
    def provide_current(self) -> date: ...

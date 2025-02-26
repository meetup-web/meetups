from abc import ABC, abstractmethod
from datetime import _Date


class DateProvider(ABC):
    @abstractmethod
    def provide_current(self) -> _Date: ...

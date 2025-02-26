from abc import ABC, abstractmethod
from collections.abc import Iterable


class Specification[T](ABC):
    @abstractmethod
    def satisfyied_by(self, candidate: T) -> bool: ...


class Result[T](ABC):
    @abstractmethod
    def first(self) -> T | None: ...
    @abstractmethod
    def all(self) -> Iterable[T]: ...

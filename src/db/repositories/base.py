from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar


T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    def create(self, entity: T) -> int:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        raise NotImplementedError



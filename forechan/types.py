from __future__ import annotations

from abc import abstractmethod, abstractproperty
from typing import (
    Any,
    AsyncContextManager,
    AsyncIterable,
    Protocol,
    Sized,
    TypeVar,
    runtime_checkable,
)

T = TypeVar("T")


class ChanClosed(Exception):
    pass


@runtime_checkable
class Chan(Sized, AsyncIterable[T], AsyncContextManager, Protocol[T]):
    @abstractproperty
    def maxlen(self) -> int:
        ...

    @abstractmethod
    def __bool__(self) -> bool:
        ...

    @abstractmethod
    async def __aenter__(self) -> Chan[T]:
        ...

    @abstractmethod
    async def __aexit__(self, *_: Any) -> None:
        ...

    @abstractmethod
    async def __anext__(self) -> T:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    @abstractmethod
    async def send(self, item: T) -> None:
        ...

    @abstractmethod
    async def recv(self) -> T:
        ...


@runtime_checkable
class WaitGroup(Sized, AsyncContextManager[None], Protocol):
    @abstractmethod
    async def wait(self) -> None:
        ...

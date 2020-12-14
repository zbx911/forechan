from __future__ import annotations

from abc import abstractmethod, abstractproperty
from typing import (
    AsyncContextManager,
    AsyncIterable,
    Awaitable,
    ContextManager,
    Protocol,
    Sized,
    TypeVar,
    runtime_checkable,
)

T = TypeVar("T")


class ChanClosed(Exception):
    pass


class ChanEmpty(Exception):
    pass


class ChanFull(Exception):
    pass


@runtime_checkable
class Chan(Sized, AsyncIterable[T], AsyncContextManager[None], Protocol[T]):
    @abstractproperty
    def maxlen(self) -> int:
        ...

    @abstractmethod
    def __bool__(self) -> bool:
        ...

    @abstractmethod
    async def __anext__(self) -> T:
        ...

    @abstractmethod
    def __lshift__(self, item: T) -> Awaitable[None]:
        ...

    @abstractmethod
    def empty(self) -> bool:
        ...

    @abstractmethod
    def full(self) -> bool:
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

    @abstractmethod
    async def _closed_notif(self) -> None:
        ...

    @abstractmethod
    async def _sendable_notif(self) -> None:
        ...

    @abstractmethod
    async def _recvable_notif(self) -> None:
        ...


@runtime_checkable
class WaitGroup(Sized, ContextManager[None], Protocol):
    @abstractmethod
    async def wait(self) -> None:
        ...

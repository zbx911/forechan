from __future__ import annotations

from abc import abstractmethod
from typing import (
    Any,
    AsyncContextManager,
    AsyncIterable,
    ContextManager,
    Iterable,
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
class Sizeable(Protocol):
    @abstractmethod
    def empty(self) -> bool:
        ...

    @abstractmethod
    def full(self) -> bool:
        ...


@runtime_checkable
class Chan(Sized, Sizeable, AsyncIterable[T], AsyncContextManager, Protocol[T]):
    @abstractmethod
    def __bool__(self) -> bool:
        ...

    @abstractmethod
    async def __aenter__(self) -> Chan[T]:
        ...

    @abstractmethod
    async def __anext__(self) -> T:
        ...

    @abstractmethod
    def __lt__(self, item: T) -> None:
        ...

    @abstractmethod
    def __gt__(self, _: Any) -> T:
        ...

    @abstractmethod
    async def __lshift__(self, item: T) -> None:
        ...

    @abstractmethod
    async def __rlshift__(self, _: Any) -> T:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    @abstractmethod
    def try_peek(self) -> T:
        ...

    @abstractmethod
    def try_send(self, item: T) -> None:
        ...

    @abstractmethod
    async def send(self, item: T) -> None:
        ...

    @abstractmethod
    def try_recv(self) -> T:
        ...

    @abstractmethod
    async def recv(self) -> T:
        ...

    @abstractmethod
    async def _on_closed(self) -> None:
        ...

    @abstractmethod
    async def _on_sendable(self) -> None:
        ...

    @abstractmethod
    async def _on_recvable(self) -> None:
        ...


@runtime_checkable
class Buf(Sized, Sizeable, Iterable[T], Protocol[T]):
    @property
    @abstractmethod
    def maxlen(self) -> int:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @abstractmethod
    def send(self, item: T) -> None:
        ...

    @abstractmethod
    def recv(self) -> T:
        ...


@runtime_checkable
class WaitGroup(Sized, ContextManager[None], Protocol):
    @abstractmethod
    async def wait(self) -> None:
        ...

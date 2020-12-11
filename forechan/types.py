from __future__ import annotations

from abc import abstractmethod, abstractproperty
from typing import (
    Any,
    AsyncContextManager,
    AsyncIterable,
    Awaitable,
    Callable,
    Protocol,
    Sized,
    TypeVar,
    runtime_checkable,
)

T = TypeVar("T")


class ChannelClosed(Exception):
    pass


Notifier = Callable[[], Awaitable[None]]
Unsub = Callable[[], None]


@runtime_checkable
class Channel(Sized, AsyncIterable[T], AsyncContextManager, Protocol[T]):
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
    async def __aenter__(self) -> Channel[T]:
        ...

    @abstractmethod
    async def __aexit__(self, *_: Any) -> None:
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
    def _on_send(self, notif: Notifier) -> Unsub:
        pass

    @abstractmethod
    def _on_recv(self, notif: Notifier) -> Unsub:
        pass

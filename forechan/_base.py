from asyncio.locks import Condition
from asyncio.tasks import gather
from typing import Any, AsyncIterator, MutableSet, TypeVar
from weakref import WeakSet

from .types import Channel, ChannelClosed, Notifier, Unsub

T = TypeVar("T")


class BaseChan(Channel[T], AsyncIterator[T]):
    def __init__(self) -> None:
        self._ss: MutableSet[Notifier] = WeakSet()
        self._rs: MutableSet[Notifier] = WeakSet()

    async def __aenter__(self) -> Channel[T]:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        try:
            return await self.recv()
        except ChannelClosed:
            raise StopAsyncIteration()

    async def _on_send(self, notif: Notifier) -> Unsub:
        self._ss.add(notif)
        return lambda: self._ss.remove(notif)

    async def _on_recv(self, notif: Notifier) -> Unsub:
        self._rs.add(notif)
        return lambda: self._rs.remove(notif)


class LockedBaseChan(BaseChan[T]):
    def __init__(self) -> None:
        self._sc = Condition()
        self._rc = Condition()

    async def close(self) -> None:
        async def c1() -> None:
            async with self._sc:
                self._sc.notify_all()

        async def c2() -> None:
            async with self._rc:
                self._rc.notify_all()

        await gather(c1(), c2())

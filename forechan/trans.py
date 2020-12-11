from asyncio import gather
from collections import deque
from typing import AsyncIterator, Callable, Deque, Generic, TypeVar

from ._base import LockedBaseChan
from .types import Channel, ChannelClosed

T = TypeVar("T")
U = TypeVar("U")


class _TransChan(LockedBaseChan[T], Generic[T, U]):
    def __init__(
        self,
        trans: Callable[[AsyncIterator[U]], AsyncIterator[T]],
        chan: Channel[U],
    ) -> None:
        super().__init__()
        self._it = trans(chan)
        self._p = chan
        self._q: Deque[T] = deque()

    @property
    def maxlen(self) -> int:
        return self._p.maxlen

    def __bool__(self) -> bool:
        return bool(self._p)

    def __len__(self) -> int:
        return len(self._p) + len(self._q)

    async def close(self) -> None:
        await gather(super().close(), self._p.close())
        self._q.clear()

    async def send(self, item: T) -> None:
        async with self._sc:
            if not self:
                raise ChannelClosed()
            elif len(self) < self.maxlen:
                async with self._rc:
                    self._rc.notify()
                    self._q.append(item)
            else:
                await self._sc.wait()
                async with self._rc:
                    if not self:
                        raise ChannelClosed()
                    else:
                        self._rc.notify()
                        self._q.append(item)

    async def _recv(self) -> T:
        if not self:
            raise ChannelClosed()
        elif len(self._p):
            async with self._sc:
                self._sc.notify()
                try:
                    return await self._it.__anext__()
                except StopAsyncIteration:
                    raise RuntimeError()
        elif len(self._q):
            async with self._sc:
                self._sc.notify()
                return self._q.popleft()
        else:
            await self._rc.wait()
            return await self._recv()

    async def recv(self) -> T:
        async with self._rc:
            return await self._recv()


def trans(
    trans: Callable[[AsyncIterator[T]], AsyncIterator[U]],
    chan: Channel[T],
) -> Channel[U]:
    return _TransChan(trans, chan=chan)

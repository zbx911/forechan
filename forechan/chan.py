from asyncio.locks import Condition
from asyncio.tasks import gather
from collections import deque
from math import inf
from typing import Deque, TypeVar

from ._base import BaseChan
from .types import ChannelClosed

T = TypeVar("T")


class Chan(BaseChan[T]):
    def __init__(self, maxlen: int = 1) -> None:
        self._closed = False
        self._sc = Condition()
        self._rc = Condition()
        self._q: Deque[T] = deque(maxlen=max(1, maxlen))

    def __bool__(self) -> bool:
        return not self._closed

    def __len__(self) -> int:
        if self:
            return len(self._q)
        else:
            return 0

    async def close(self) -> None:
        async def c1() -> None:
            async with self._sc:
                self._sc.notify_all()

        async def c2() -> None:
            async with self._rc:
                self._rc.notify_all()

        self._closed = True
        await gather(c1(), c2())

    async def send(self, item: T) -> None:
        async with self._sc:
            if not self:
                raise ChannelClosed()
            elif len(self) < (self._q.maxlen or inf):
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

    async def recv(self) -> T:
        async with self._rc:
            if not self:
                raise ChannelClosed()
            elif len(self):
                async with self._sc:
                    self._sc.notify()
                    return self._q.popleft()
            else:
                await self._rc.wait()
                async with self._sc:
                    if not self:
                        raise ChannelClosed()
                    else:
                        self._sc.notify()
                        return self._q.popleft()

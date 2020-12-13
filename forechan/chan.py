from asyncio.locks import Condition
from asyncio.tasks import gather
from collections import deque
from typing import Any, AsyncIterator, Deque, Type, TypeVar, cast

from .types import Channel, ChannelClosed

T = TypeVar("T")


class _Chan(Channel[T], AsyncIterator[T]):
    def __init__(self, maxlen: int) -> None:
        super().__init__()
        self._q: Deque[T] = deque(maxlen=max(1, maxlen))
        self._closed = False
        self._sc = Condition()
        self._rc = Condition()

    @property
    def maxlen(self) -> int:
        return cast(int, self._q.maxlen)

    def __bool__(self) -> bool:
        return not self._closed

    def __len__(self) -> int:
        return len(self._q)

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

    async def close(self) -> None:
        async def c1() -> None:
            async with self._sc:
                self._sc.notify_all()

        async def c2() -> None:
            async with self._rc:
                self._rc.notify_all()

        self._closed = True
        self._q.clear()
        await gather(c1(), c2())

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


def mk_chan(t: Type[T], maxlen: int = 1) -> Channel[T]:
    return _Chan[T](maxlen=maxlen)

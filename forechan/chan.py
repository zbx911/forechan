from asyncio.locks import Condition, Event
from asyncio.tasks import gather
from collections import deque
from contextlib import contextmanager
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Deque,
    Iterator,
    Optional,
    Type,
    TypeVar,
    cast,
)

from .types import Chan, ChanClosed

T = TypeVar("T")


class _Chan(Chan[T], AsyncIterator[T]):
    def __init__(self, maxlen: int) -> None:
        super().__init__()
        self._q: Deque[T] = deque(maxlen=max(1, maxlen))
        self._sc, self._rc = Condition(), Condition()
        self._nc, self._ns, self._nr = Event(), Event(), Event()

    @property
    def maxlen(self) -> int:
        return cast(int, self._q.maxlen)

    def __bool__(self) -> bool:
        return not self._nc.is_set()

    def __len__(self) -> int:
        return len(self._q)

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        try:
            return await self.recv()
        except ChanClosed:
            raise StopAsyncIteration()

    def __lshift__(self, item: T) -> Awaitable[None]:
        return self.send(item)

    def __neg__(self) -> Awaitable[T]:
        return self.recv()

    async def close(self) -> None:
        async def c1() -> None:
            async with self._sc:
                self._sc.notify_all()

        async def c2() -> None:
            async with self._rc:
                self._rc.notify_all()

        self._nc.set()
        self._q.clear()
        await gather(c1(), c2())

    @contextmanager
    def _sent_handler(self) -> Iterator[None]:
        try:
            yield None
        finally:
            self._nr.set()
            if len(self) >= self.maxlen:
                self._ns.clear()

    @contextmanager
    def _recv_handler(self) -> Iterator[None]:
        try:
            yield None
        finally:
            self._ns.set()
            if not len(self):
                self._nr.clear()

    async def send(self, item: T) -> None:
        with self._sent_handler():
            async with self._sc:
                if not self:
                    raise ChanClosed()
                elif len(self) < self.maxlen:
                    async with self._rc:
                        self._rc.notify()
                        self._q.append(item)
                else:
                    await self._sc.wait()
                    async with self._rc:
                        if not self:
                            raise ChanClosed()
                        else:
                            self._rc.notify()
                            self._q.append(item)

    async def recv(self) -> T:
        with self._recv_handler():
            async with self._rc:
                if not self:
                    raise ChanClosed()
                elif len(self):
                    async with self._sc:
                        self._sc.notify()
                        return self._q.popleft()
                else:
                    await self._rc.wait()
                    async with self._sc:
                        if not self:
                            raise ChanClosed()
                        else:
                            self._sc.notify()
                            return self._q.popleft()

    async def _closed_notif(self) -> None:
        await self._nc.wait()

    async def _sendable_notif(self) -> None:
        await self._ns.wait()

    async def _recvable_notif(self) -> None:
        await self._nr.wait()


def chan(t: Optional[Type[T]] = None, maxlen: int = 1) -> Chan[T]:
    return _Chan[T](maxlen=maxlen)

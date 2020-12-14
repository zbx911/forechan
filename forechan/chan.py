from asyncio.locks import Condition, Event
from asyncio.tasks import gather
from collections import deque
from contextlib import contextmanager
from typing import (
    Any,
    AsyncIterator,
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
        self._ns.set()

    @property
    def maxlen(self) -> int:
        return cast(int, self._q.maxlen)

    def __str__(self) -> str:
        return f"chan[{', '.join(str(item) for item in self._q)}]"

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

    async def __lshift__(self, item: T) -> None:
        await self.send(item)

    async def __rlshift__(self, _: Any) -> T:
        return await self.recv()

    def empty(self) -> bool:
        return not len(self)

    def full(self) -> bool:
        return len(self) >= self.maxlen

    async def close(self) -> None:
        async def c1() -> None:
            async with self._sc:
                self._ns.set()
                self._sc.notify_all()

        async def c2() -> None:
            async with self._rc:
                self._nr.set()
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
            if self.full():
                self._ns.clear()

    @contextmanager
    def _recv_handler(self) -> Iterator[None]:
        try:
            yield None
        finally:
            self._ns.set()
            if self.empty():
                self._nr.clear()

    async def send(self, item: T) -> None:
        with self._sent_handler():
            async with self._sc:
                if not self:
                    raise ChanClosed()
                elif not self.full():
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
                elif not self.empty():
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
        if not self:
            raise ChanClosed()

    async def _recvable_notif(self) -> None:
        await self._nr.wait()
        if not self:
            raise ChanClosed()


def chan(t: Optional[Type[T]] = None, maxlen: int = 1) -> Chan[T]:
    return _Chan[T](maxlen=maxlen)

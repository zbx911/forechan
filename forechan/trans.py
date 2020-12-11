from asyncio.tasks import gather
from typing import AsyncIterator, Callable, Generic, TypeVar

from ._base import BaseChan
from .chan import Chan
from .types import Channel, ChannelClosed

T = TypeVar("T")
U = TypeVar("U")


class _TransChan(BaseChan[T], Generic[T, U]):
    def __init__(
        self,
        trans: Callable[[AsyncIterator[U]], AsyncIterator[T]],
        chan: Channel[U],
    ) -> None:
        self._q = chan
        self._buf: Channel[T] = Chan[T]()
        self._it = trans(chan)

    @property
    def maxlen(self) -> int:
        return 2

    def __bool__(self) -> bool:
        return bool(self._q and self._buf)

    def __len__(self) -> int:
        return len(self._q) + len(self._buf)

    async def close(self) -> None:
        await gather(self._q.close(), self._buf.close())

    async def send(self, item: T) -> None:
        await self._buf.send(item)

    async def recv(self) -> T:
        async def cont() -> T:
            try:
                return await self._it.__anext__()
            except StopAsyncIteration:
                raise RuntimeError()

        if not self:
            raise ChannelClosed()
        elif len(self._q):
            return await cont()
        elif len(self._buf):
            return await self._buf.recv()
        else:
            return await cont()


def trans(
    trans: Callable[[AsyncIterator[T]], AsyncIterator[U]],
    chan: Channel[T],
) -> Channel[U]:
    return _TransChan(trans, chan=chan)

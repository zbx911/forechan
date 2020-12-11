from asyncio import gather
from collections import deque
from typing import Any, Deque, Sequence, Tuple, TypeVar, cast

from ._base import BaseChan
from .types import Channel, ChannelClosed

T = TypeVar("T")


class _SelectChan(BaseChan[T]):
    def __init__(
        self,
        chan: Channel[Any],
        *chans: Channel[Any],
    ) -> None:
        super().__init__()
        self._ps: Sequence[Channel[Any]] = tuple((chan, *chans))
        self._q: Deque[T] = deque(maxlen=max(ch.maxlen for ch in self._ps))

    @property
    def maxlen(self) -> int:
        return cast(int, self._q.maxlen)

    def __bool__(self) -> bool:
        return any(self._ps)

    def __len__(self) -> int:
        return sum(len(p) for p in self._ps)

    async def close(self) -> None:
        await gather(*(p.close() for p in self._ps))

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
        pass


def select(
    chan: Channel[Any], *chans: Channel[Any]
) -> Channel[Tuple[Channel[Any], Any]]:
    return _SelectChan(chan, *chans)

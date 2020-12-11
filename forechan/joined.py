from asyncio import FIRST_COMPLETED, wait
from asyncio.futures import Future
from asyncio.tasks import gather
from collections import deque
from itertools import chain
from typing import Awaitable, Deque, Set, Sized, Tuple, TypeVar, cast

from ._base import BaseChan
from .types import Channel, Deque, Set, TypeVar

T, U = TypeVar("T"), TypeVar("U")


async def _with_ctx(ctx: T, co: Awaitable[U]) -> Tuple[T, U]:
    return (ctx, await co)


class _JoinedChan(BaseChan[T]):
    def __init__(self, chan: Channel[T], *chans: Channel[T]) -> None:
        self._chans: Set[Channel[T]] = {chan, *chans}
        self._available_ch: Set[Channel] = set()
        self._done: Deque[T] = deque()
        self._pending: Set[Future[Tuple[Channel[T], T]]] = set()

    def __bool__(self) -> bool:
        return all(chan for chan in self._chans)

    def __len__(self) -> int:
        return sum(map(len, (cast(Sized, self._done), *self._chans)))

    async def close(self) -> None:
        await gather(*(chan.close() for chan in self._chans))
        for mut_seq in (self._chans, self._available_ch, self._done, self._pending):
            mut_seq.clear()

    async def send(self, item: T) -> None:
        await gather(*(chan.send(item) for chan in self._chans))

    async def recv(self) -> T:
        if not self._done:
            done, pending = await wait(
                chain(
                    self._pending,
                    (
                        _with_ctx(chan, co=chan.recv())
                        for chan in self._chans
                        if chan in self._available_ch
                    ),
                ),
                return_when=FIRST_COMPLETED,
            )

            self._pending = pending
            self._available_ch.clear()
            for co in done:
                chan, item = await co
                self._available_ch.add(chan)
                self._done.append(item)

        return self._done.popleft()


def join(chan: Channel[T], *chans: Channel[T]) -> Channel[T]:
    return _JoinedChan(chan, *chans)

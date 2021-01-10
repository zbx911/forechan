from asyncio.tasks import create_task, gather
from itertools import chain
from typing import Awaitable, Iterable, MutableSequence, TypeVar

from ._da import race
from .types import Chan

T = TypeVar("T")


async def pipe(src: Iterable[Chan[T]], dest: Iterable[Chan[T]]) -> None:
    """
    # each item in `src` goes to first ready ch in `dest`

     `src`       `dest`
    ------>|    |------>|
    ------>|    |------>|
    ------>|--->|------>|
    ------>|    |------>|
    ------>|    |------>|
    ...
    """

    r_chans: MutableSequence[Chan[T]] = [*src]
    s_chans: MutableSequence[Chan[T]] = [*dest]

    while r_chans and s_chans:
        (_r_ready, _, _), (_s_ready, _, _) = await gather(
            race(*(create_task(ch._on_recvable()) for ch in r_chans)),
            race(*(create_task(ch._on_sendable()) for ch in s_chans)),
        )
        r_ready, s_ready = _r_ready.result(), _s_ready.result()

        if not r_ready or not s_ready:
            r_chans[:] = [c for c in r_chans if c]
            s_chans[:] = [c for c in s_chans if c]
        elif r_ready.recvable() and s_ready.sendable():
            s_ready.try_send(r_ready.try_recv())


async def _send(fut: Awaitable[Chan[T]], item: T) -> None:
    ch = await fut
    while ch:
        await ch._on_sendable()
        if ch.sendable():
            ch.try_send(item)


async def pipe_parallel(src: Iterable[Chan[T]], dest: Iterable[Chan[T]]) -> None:
    """
    # each item in `src` goes to each ch in `dest`

     `src`       `dest`
    ------>|    |------>|
    ------>|    |------>|
    ------>|--->|------>|
    ------>|    |------>|
    ------>|    |------>|
    ...
    """

    r_chans: MutableSequence[Chan[T]] = [*src]
    s_chans: MutableSequence[Chan[T]] = [*dest]

    while r_chans and s_chans:
        (_r_ready, _, _), (_s_ready, s_done, s_pending) = await gather(
            race(*(create_task(ch._on_recvable()) for ch in r_chans)),
            race(*(create_task(ch._on_sendable()) for ch in s_chans)),
        )
        r_ready, s_ready = _r_ready.result(), _s_ready.result()

        if not r_ready or not s_ready:
            r_chans[:] = [c for c in r_chans if c]
            s_chans[:] = [c for c in s_chans if c]
        elif r_ready.recvable() and s_ready.sendable():
            item = r_ready.try_recv()
            s_ready.try_send(item)
            await gather(*(_send(fut, item=item) for fut in chain(s_done, s_pending)))

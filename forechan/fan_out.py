from asyncio.tasks import gather
from itertools import islice
from typing import Awaitable, MutableSequence, Sequence, TypeVar

from ._da import race
from .chan import chan
from .go import GO, go
from .ops import with_aclosing
from .types import Chan

T = TypeVar("T")


async def _send(fut: Awaitable[Chan[T]], item: T) -> None:
    ch = await fut
    while ch:
        await ch._on_sendable()
        if ch.sendable():
            ch.try_send(item)


async def fan_out(
    ch: Chan[T], n: int, cascade_close: bool = True, go: GO = go
) -> Sequence[Chan[T]]:
    """
    # each item from `ch` goes to each chan in `out`

           `out`
           |------>
     `ch`  |------>
    ------>|------>
           |------>
           |------>
           ...
    """

    if n < 1:
        raise ValueError()

    cs: MutableSequence[Chan[T]] = [*islice(iter(chan, None), n)]
    out: Sequence[Chan[T]] = tuple(cs)

    async def cont() -> None:
        async with with_aclosing(*out):
            async with with_aclosing(ch, close=cascade_close):
                while ch and cs:
                    _, (ready, pending) = await gather(
                        ch._on_recvable(),
                        race(*(c._on_sendable() for c in cs)),
                    )
                    if not ready:
                        cs[:] = [c for c in cs if c]
                    elif ch.recvable() and ready.sendable():
                        item = ch.try_recv()
                        ready.try_send(item)
                        await gather(*(_send(fut, item=item) for fut in pending))

    await go(cont())
    return out

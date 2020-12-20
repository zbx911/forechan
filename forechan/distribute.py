from asyncio.tasks import gather
from typing import MutableSequence, TypeVar

from ._da import race
from .go import GO, go
from .ops import with_aclosing
from .types import Chan

T = TypeVar("T")


async def distribute(
    src: Chan[T], *dest: Chan[T], cascade_close: bool = True, go: GO = go
) -> None:
    """
    # each item from `src` goes to first available chan in `*dest`

           `*dest`
           |------>
     `src` |------>
    ------>|------>
           |------>
           |------>
           ...
    """

    cs: MutableSequence[Chan[T]] = [*dest]

    async def cont() -> None:
        async with with_aclosing(src, *dest, close=cascade_close):
            while src and cs:
                _, (ready, _) = await gather(
                    src._on_recvable(),
                    race(*(ch._on_sendable() for ch in cs)),
                )
                if not ready:
                    cs[:] = [ch for ch in cs if ch]
                elif src.recvable() and ready.sendable():
                    ready.try_send(src.try_recv())

    await go(cont())

from asyncio.tasks import gather
from typing import Iterable, MutableSequence, TypeVar

from ._da import race
from .go import GO, go
from .ops import with_aclosing
from .types import Chan

T = TypeVar("T")


async def pipe(
    src: Iterable[Chan[T]], dest: Chan[T], cascade_close: bool = True, go: GO = go
) -> None:
    """
    # each item in `*src` goes to `dest`

    `*src`
    ------>|
    ------>|
    ------>|---> `dest`
    ------>|
    ------>|
    ...
    """

    channels: MutableSequence[Chan[T]] = [*src]

    async def cont() -> None:
        async with dest:
            async with with_aclosing(*src, dest, close=cascade_close):
                while dest and channels:
                    (ready, _), _ = await gather(
                        race(*(ch._on_recvable() for ch in channels)),
                        dest._on_sendable(),
                    )
                    if not ready:
                        channels[:] = [ch for ch in channels if ch]
                    elif ready.recvable() and dest.sendable():
                        dest.try_send(ready.try_recv())

    await go(cont())

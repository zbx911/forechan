from asyncio.tasks import create_task
from typing import AsyncIterator, Callable, TypeVar

from ._ops import close
from .chan import chan
from .types import Chan, ChanClosed

T = TypeVar("T")
U = TypeVar("U")


async def trans(
    trans: Callable[[AsyncIterator[T]], AsyncIterator[U]],
    ch: Chan[T],
    cascade_close: bool = True,
) -> Chan[U]:
    out: Chan[U] = chan()

    async def close_upstream() -> None:
        await out._closed_notif()
        await close(ch, close=cascade_close)

    create_task(close_upstream())

    async def cont() -> None:
        async with out:
            async for item in trans(ch):
                try:
                    await out.send(item)
                except ChanClosed:
                    break

    create_task(cont())
    return out

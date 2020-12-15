from asyncio.tasks import create_task
from typing import AsyncIterator, Callable, TypeVar

from .ops import cascading_close
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

    if cascade_close:
        await cascading_close((out,), dest=(ch,))

    async def cont() -> None:
        async with out:
            async for item in trans(ch):
                try:
                    await out.send(item)
                except ChanClosed:
                    break

    create_task(cont())
    return out

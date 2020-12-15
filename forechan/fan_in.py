from asyncio.tasks import create_task
from typing import TypeVar

from .chan import chan
from .ops import cascading_close
from .select import select
from .types import Chan, ChanClosed

T = TypeVar("T")


async def fan_in(ch: Chan[T], *chs: Chan[T], cascade_close: bool = True) -> Chan[T]:
    out: Chan[T] = chan()

    if cascade_close:
        await cascading_close((out,), dest=(ch, *chs))

    async def cont() -> None:
        async with out:
            async for _, item in await select(ch, *chs):
                try:
                    await out.send(item)
                except ChanClosed:
                    break

    create_task(cont())
    return out

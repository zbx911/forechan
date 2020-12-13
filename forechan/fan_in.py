from asyncio.tasks import create_task
from typing import Any, Sequence, TypeVar

from .chan import chan
from .operations import close
from .select import select
from .types import Chan, ChanClosed

T = TypeVar("T")


async def fan_in(ch: Chan[T], *chs: Chan[T], cascade_close: bool = True) -> Chan[T]:
    channels: Sequence[Chan[Any]] = tuple((ch, *chs))
    out: Chan[T] = chan()

    async def close_upstream() -> None:
        await out._closed_notif()
        await close(ch, *chs, close=cascade_close)

    create_task(close_upstream())

    async def cont() -> None:
        async with out:
            async for _, item in await select(*channels):
                try:
                    await out.send(item)
                except ChanClosed:
                    break

    create_task(cont())
    return out

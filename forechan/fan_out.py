from asyncio.tasks import create_task, gather
from itertools import islice
from typing import Sequence, Set, TypeVar

from ._ops import close
from .chan import chan
from .types import Chan, ChanClosed
from .wait_group import wait_group

T = TypeVar("T")


async def fan_out(ch: Chan[T], n: int, cascade_close: bool = True) -> Sequence[Chan[T]]:
    if n < 1:
        raise ValueError()

    channels: Set[Chan[T]] = {*islice(iter(chan, None), n)}
    wg = wait_group()
    ret = tuple(channels)

    for out in channels:

        async def wg_downstream() -> None:
            with wg:
                await out._closed_notif()
                channels.remove(out)

        create_task(wg_downstream())

    async def close_upstream() -> None:
        await wg.wait()
        await close(ch, close=cascade_close)

    create_task(close_upstream())

    async def cont() -> None:
        async for item in ch:

            async def send(out: Chan[T]) -> None:
                try:
                    await out.send(item)
                except ChanClosed:
                    raise

            if channels:
                await gather(*map(send, channels))
            else:
                break

    create_task(cont())
    return ret

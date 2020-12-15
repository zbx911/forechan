from asyncio.tasks import create_task, gather
from itertools import islice
from typing import Sequence, Set, TypeVar

from ._ops import cascading_close
from .chan import chan
from .types import Chan, ChanClosed

T = TypeVar("T")


async def fan_out(ch: Chan[T], n: int, cascade_close: bool = True) -> Sequence[Chan[T]]:
    if n < 1:
        raise ValueError()

    channels: Set[Chan[T]] = {*islice(iter(chan, None), n)}
    ret = tuple(channels)
    if cascade_close:
        await cascading_close(channels, dest=(ch,))
    await cascading_close((ch,), dest=channels)

    async def cont() -> None:
        async for item in ch:

            async def send(out: Chan[T]) -> None:
                try:
                    await out.send(item)
                except ChanClosed:
                    channels.remove(out)

            if channels:
                await gather(*map(send, channels))
            else:
                break

    create_task(cont())
    return ret

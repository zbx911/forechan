from asyncio.tasks import create_task, gather
from itertools import islice
from typing import MutableSequence, Sequence, Set, TypeVar

from .ops import cascading_close
from .chan import chan
from .types import Chan, ChanClosed

T = TypeVar("T")


async def fan_out(ch: Chan[T], n: int, cascade_close: bool = True) -> Sequence[Chan[T]]:
    if n < 1:
        raise ValueError()

    out: MutableSequence[Chan[T]] = [*islice(iter(chan, None), n)]
    ret: Sequence[Chan[T]] = tuple(out)

    if cascade_close:
        await cascading_close(out, dest=(ch,))
    await cascading_close((ch,), dest=out)

    async def cont() -> None:
        while True:
            try:
                await gather(ch._on_recvable(), *(c._on_sendable() for c in out))
            except ChanClosed:
                if not ch:
                    break
                else:
                    out[:] = [c for c in out if c]
            else:
                if ch._recvable() and all(c._sendable() for c in out):
                    item = ch.try_recv()
                    for c in out:
                        c.try_send(item)

    create_task(cont())
    return ret

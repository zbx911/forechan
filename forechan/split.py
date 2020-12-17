from asyncio import gather
from asyncio.tasks import create_task
from typing import Callable, Tuple, TypeVar

from .chan import chan
from .ops import cascading_close
from .types import Chan, ChanClosed

T = TypeVar("T")


async def split(
    predicate: Callable[[T], bool],
    ch: Chan[T],
    cascade_close: bool = True,
) -> Tuple[Chan[T], Chan[T]]:
    lhs: Chan[T] = chan()
    rhs: Chan[T] = chan()

    if cascade_close:
        await cascading_close((lhs, rhs), dest=(ch,))
    await gather(
        cascading_close((ch,), dest=(lhs, rhs)),
        cascading_close((lhs,), dest=(rhs,)),
        cascading_close((rhs,), dest=(lhs,)),
    )

    async def cont() -> None:
        while True:
            try:
                await gather(ch._on_recvable(), lhs._on_sendable(), rhs._on_sendable())
            except ChanClosed:
                break
            else:
                if ch._recvable() and lhs._sendable() and rhs._sendable():
                    item = ch.try_recv()
                    det = predicate(item)
                    if det:
                        lhs.try_send(item)
                    else:
                        rhs.try_send(item)

    create_task(cont())
    return lhs, rhs

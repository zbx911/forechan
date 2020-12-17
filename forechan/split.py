from asyncio import gather
from asyncio.tasks import create_task
from typing import Callable, Tuple, TypeVar

from .chan import chan
from .ops import with_closing
from .types import Chan

T = TypeVar("T")


async def split(
    predicate: Callable[[T], bool],
    ch: Chan[T],
    cascade_close: bool = True,
) -> Tuple[Chan[T], Chan[T]]:
    lhs: Chan[T] = chan()
    rhs: Chan[T] = chan()

    async def cont() -> None:
        async with with_closing(lhs, rhs):
            async with with_closing(ch, close=cascade_close):
                while ch and lhs and rhs:
                    await gather(
                        ch._on_recvable(), lhs._on_sendable(), rhs._on_sendable()
                    )
                    if ch.recvable() and lhs.sendable() and rhs.sendable():
                        item = ch.try_recv()
                        det = predicate(item)
                        if det:
                            lhs.try_send(item)
                        else:
                            rhs.try_send(item)

    create_task(cont())
    return lhs, rhs

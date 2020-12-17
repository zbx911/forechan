from asyncio import gather
from asyncio.tasks import create_task
from typing import Sequence, TypeVar

from .ops import cascading_close
from .types import Chan, ChanClosed

T = TypeVar("T")


async def pipe(
    src: Sequence[Chan[T]],
    dest: Chan[T],
    cascade_close: bool = True,
) -> None:
    if cascade_close:
        await gather(
            cascading_close(src, dest=(dest,)), cascading_close((dest,), dest=src)
        )

    for ch in src:

        async def cont() -> None:
            while True:
                try:
                    await gather(ch._on_recvable(), dest._on_sendable())
                except ChanClosed:
                    break
                else:
                    if ch._recvable() and dest._sendable():
                        item = ch.try_recv()
                        dest.try_send(item)

        create_task(cont())

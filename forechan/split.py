from asyncio import gather
from asyncio.tasks import create_task
from typing import Awaitable, Callable, Tuple, TypeVar

from .ops import cascading_close
from .chan import chan
from .types import Chan

T = TypeVar("T")


async def split(
    predicate: Callable[[T], Awaitable[bool]],
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
        async for item in ch:
            det = await predicate(item)
            if det:
                await lhs.send(item)
            else:
                await rhs.send(item)

    create_task(cont())
    return lhs, rhs

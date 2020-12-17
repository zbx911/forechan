from asyncio.tasks import create_task
from typing import AsyncIterator, Callable, TypeVar

from .chan import chan
from .ops import with_closing
from .types import Chan

T = TypeVar("T")
U = TypeVar("U")


async def trans(
    trans: Callable[[AsyncIterator[T]], AsyncIterator[U]],
    ch: Chan[T],
    cascade_close: bool = True,
) -> Chan[U]:
    out: Chan[U] = chan()

    async def cont() -> None:
        async with out:
            async with with_closing(ch, close=cascade_close):
                async for item in trans(ch):
                    while out:
                        await out._on_sendable()
                        if out.sendable():
                            out.try_send(item)
                            break
                    if not out:
                        break

    create_task(cont())
    return out

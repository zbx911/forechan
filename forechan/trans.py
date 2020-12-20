from typing import AsyncIterator, Callable, TypeVar

from ._sched import go
from .chan import chan
from .ops import with_closing
from .types import Chan

T = TypeVar("T")
U = TypeVar("U")


async def trans(
    xform: Callable[[AsyncIterator[T]], AsyncIterator[U]],
    ch: Chan[T],
    cascade_close: bool = True,
) -> Chan[U]:
    """
     `ch`               `out`
    ------>|[transform]|------>
    """

    out: Chan[U] = chan()

    async def cont() -> None:
        async with out:
            async with with_closing(ch, close=cascade_close):
                async for item in xform(ch):
                    while out:
                        await out._on_sendable()
                        if out.sendable():
                            out.try_send(item)
                            break
                    else:
                        break

    await go(cont())
    return out

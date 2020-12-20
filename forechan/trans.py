from typing import AsyncIterator, Callable, TypeVar

from .chan import chan
from .go import GO, go
from .ops import with_aclosing
from .types import Chan

T = TypeVar("T")
U = TypeVar("U")


async def trans(
    xform: Callable[[AsyncIterator[T]], AsyncIterator[U]],
    ch: Chan[T],
    cascade_close: bool = True,
    go: GO = go,
) -> Chan[U]:
    """
     `ch`               `out`
    ------>|[transform]|------>
    """

    out: Chan[U] = chan()

    async def cont() -> None:
        async with out:
            async with with_aclosing(ch, close=cascade_close):
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

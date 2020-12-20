from asyncio.tasks import gather
from typing import Any, MutableSequence, Tuple

from ._da import race
from ._sched import go
from .chan import chan
from .ops import with_closing
from .types import Chan


async def select(
    *cs: Chan[Any], cascade_close: bool = True
) -> Chan[Tuple[Chan[Any], Any]]:
    """
    async for ch, item in await select(ch1, ch2, ch3, ...):
    if ch == ch1:
        ...
    elif ch == ch2:
        ...
    elif ch == ch3:
        ...
    """

    out: Chan[Any] = chan()
    channels: MutableSequence[Chan[Any]] = [*cs]

    async def cont() -> None:
        async with out:
            async with with_closing(*cs, close=cascade_close):
                while out and channels:
                    (ready, _), _ = await gather(
                        race(*(ch._on_recvable() for ch in channels)),
                        out._on_sendable(),
                    )
                    if not ready:
                        channels[:] = [ch for ch in channels if ch]
                    elif ready.recvable() and out.sendable():
                        out.try_send((ready, ready.try_recv()))

    await go(cont())
    return out

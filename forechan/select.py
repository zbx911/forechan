from asyncio.tasks import create_task, gather
from typing import Any, MutableSequence, Tuple

from ._da import race
from .chan import chan
from .ops import with_closing
from .types import Chan


async def select(
    *cs: Chan[Any], cascade_close: bool = True
) -> Chan[Tuple[Chan[Any], Any]]:
    out: Chan[Any] = chan()
    channels: MutableSequence[Chan[Any]] = [*cs]

    async def cont() -> None:
        async with out:
            async with with_closing(*cs, close=cascade_close):
                while out and channels:
                    _, (ready, _) = await gather(
                        out._on_sendable(),
                        race(*(ch._on_recvable() for ch in channels)),
                    )
                    if not ready:
                        channels[:] = [ch for ch in channels if ch]
                    elif out.sendable() and ready.recvable():
                        out.try_send(ready.try_recv())

    create_task(cont())
    return out

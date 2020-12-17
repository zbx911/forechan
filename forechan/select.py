from asyncio.tasks import create_task, gather
from typing import Any, MutableSequence, Tuple

from ._da import race
from .chan import chan
from .ops import with_closing
from .types import Chan, ChanClosed


async def select(ch: Chan[Any], *chs: Chan[Any]) -> Chan[Tuple[Chan[Any], Any]]:
    out: Chan[Any] = chan()
    cs: MutableSequence[Chan[Any]] = [ch, *chs]

    async def cont() -> None:
        async with out:
            async with with_closing(*cs):
                while cs:
                    try:
                        _, (ready, _) = await gather(
                            out._on_sendable(),
                            race(*(c._on_recvable() for c in cs)),
                        )
                    except ChanClosed:
                        break
                    else:
                        if not ready:
                            cs[:] = [c for c in cs if c]
                        elif out.sendable() and ready.recvable():
                            out.try_send(ready.try_recv())

    create_task(cont())
    return out

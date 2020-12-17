from asyncio.tasks import create_task, gather, wait, FIRST_COMPLETED
from itertools import chain
from typing import Any, MutableSequence, Tuple

from .chan import chan
from .ops import cascading_close
from .types import Chan, ChanClosed


async def select(
    ch: Chan[Any], *chs: Chan[Any], cascade_close: bool = True
) -> Chan[Tuple[Chan[Any], Any]]:
    out: Chan[Any] = chan()

    if cascade_close:
        await cascading_close((out,), dest=(ch, *chs))
    await cascading_close((ch, *chs), dest=(out,))

    cs: MutableSequence[Chan[Any]] = [ch, *chs]

    async def cont() -> None:
        while out:
            try:
                _, (done, pending) = await gather(
                    out._on_sendable(),
                    wait((c._on_recvable() for c in cs), return_when=FIRST_COMPLETED),
                )
            except ChanClosed:
                cs[:] = [c for c in cs if c]
            else:
                for fut in done:
                    ch = fut.result()
                    if ch.sendable():
                            ch.try_send()

    create_task(cont())
    return out

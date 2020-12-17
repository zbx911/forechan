from asyncio.tasks import create_task, gather
from typing import Tuple, TypeVar

from .chan import chan
from .select import select
from .types import Chan

T = TypeVar("T")


async def fan_in(ch: Chan[T], *cs: Chan[T], cascade_close: bool = True) -> Chan[T]:
    upstream: Chan[Tuple[Chan[T], T]] = await select(
        ch, *cs, cascade_close=cascade_close
    )
    out: Chan[T] = chan()

    async def cont() -> None:
        async with out:
            while out and upstream:
                await gather(out._on_sendable(), upstream._on_recvable())
                if out.sendable() and upstream.recvable():
                    _, item = upstream.try_recv()
                    out.try_send(item)

    create_task(cont())
    return out

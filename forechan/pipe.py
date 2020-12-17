from asyncio.tasks import create_task, gather
from typing import Iterable, Tuple, TypeVar

from .ops import with_closing
from .select import select
from .types import Chan

T = TypeVar("T")


async def pipe(
    src: Iterable[Chan[T]], dest: Chan[T], cascade_close: bool = True
) -> None:
    upstream: Chan[Tuple[Chan[T], T]] = await select(*src)

    async def cont() -> None:
        async with with_closing(upstream, dest, close=cascade_close):
            while dest and upstream:
                await gather(dest._on_sendable(), upstream._on_recvable())
                if dest.sendable() and upstream.recvable():
                    _, item = upstream.try_recv()
                    dest.try_send(item)

    create_task(cont())

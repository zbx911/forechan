from asyncio.tasks import create_task, gather
from typing import Any, Iterable, TypeVar

from .types import Chan
from .wait_group import wait_group

T = TypeVar("T")


async def cascading_close(src: Iterable[Chan[Any]], dest: Iterable[Chan[Any]]) -> None:
    wg = wait_group()
    for ch in src:

        async def cont() -> None:
            with wg:
                await ch._closed_notif()

        create_task(cont())

    async def close() -> None:
        await gather(*(ch.close() for ch in dest))

    create_task(close())

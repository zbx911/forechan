from asyncio import gather
from asyncio.tasks import create_task
from typing import Sequence, TypeVar

from ._ops import cascading_close
from .types import Chan

T = TypeVar("T")


async def pipe(
    src: Sequence[Chan[T]],
    dest: Chan[T],
    cascade_close: bool = True,
) -> None:
    if cascade_close:
        await gather(
            cascading_close(src, dest=(dest,)), cascading_close((dest,), dest=src)
        )

    for ch in src:

        async def cont() -> None:
            async for item in ch:
                await dest.send(item)

        create_task(cont())

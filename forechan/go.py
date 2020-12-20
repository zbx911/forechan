from typing import Awaitable, Callable, TypeVar
from asyncio import create_task

T = TypeVar("T")


async def _default_sch(aw: Awaitable[T]) -> Awaitable[T]:
    return create_task(aw)


_scheduler_ = _default_sch


async def go(aw: Awaitable[T]) -> Awaitable[T]:
    return await _scheduler_(aw)


def set_scheduler(sch: Callable[[Awaitable[T]], Awaitable[Awaitable[T]]]) -> None:
    global _scheduler_
    _scheduler_ = sch
from asyncio.locks import Event
from asyncio.tasks import create_task
from itertools import count
from typing import Awaitable, Callable, MutableMapping, Optional, Tuple, Type, TypeVar

from .chan import chan
from .types import Chan

T = TypeVar("T")
U = TypeVar("U")


async def mb_from(
    ask: Chan[Tuple[int, T]], reply: Chan[Tuple[int, U]]
) -> Callable[[T], Awaitable[U]]:
    ev = Event()
    replies: MutableMapping[int, U] = {}
    it = count()

    async def cont() -> None:
        async for rid, ans in reply:
            replies[rid] = ans
            ev.set()

    create_task(cont())

    async def req(qst: T) -> U:
        uid = next(it)
        await ask.send((uid, qst))
        while True:
            await ev.wait()
            if uid in replies:
                return replies.pop(uid)

    return req


async def mb(
    t: Optional[Type[T]] = None, u: Optional[Type[U]] = None
) -> Tuple[Chan[Tuple[int, T]], Chan[Tuple[int, U]], Callable[[T], Awaitable[U]]]:
    ask: Chan[Tuple[int, T]] = chan()
    reply: Chan[Tuple[int, U]] = chan()
    req = await mb_from(ask, reply=reply)
    return ask, reply, req

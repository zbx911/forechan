from itertools import count
from typing import Awaitable, Callable, Tuple, Type, TypeVar

from .chan import chan
from .types import Chan

T = TypeVar("T")

U = TypeVar("U")


class OutdatedError(Exception):
    pass


def mk_req(
    ask: Chan[Tuple[int, T]], reply: Chan[Tuple[int, U]]
) -> Callable[[T], Awaitable[U]]:
    it = count()
    uid = -1

    async def cont(qst: T) -> U:
        nonlocal uid
        uid = next(it)

        await ask.send((uid, qst))
        while True:
            rid, ans = await reply.recv()
            if rid < uid:
                pass
            elif rid > uid:
                await reply.send((rid, ans))
                raise OutdatedError()
            else:
                return ans

    return cont

from asyncio.futures import Future
from asyncio.tasks import FIRST_COMPLETED, wait
from typing import AbstractSet, Any, MutableSet, Tuple, TypeVar, cast

_T2 = TypeVar("_T2", bound=Future)


async def race(aw: _T2, *aws: _T2) -> Tuple[_T2, AbstractSet[_T2], AbstractSet[_T2]]:
    r: Any = await wait((aw, *aws), return_when=FIRST_COMPLETED)
    done, pending = cast(Tuple[MutableSet[_T2], MutableSet[_T2]], r)
    ret = done.pop()
    return ret, done, pending

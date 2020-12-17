from asyncio import gather, wait_for
from asyncio.tasks import gather, sleep
from itertools import islice
from random import shuffle
from typing import Any, AsyncIterator, Awaitable, MutableSequence
from unittest import IsolatedAsyncioTestCase

from ...forechan.chan import chan
from ...forechan.trans import trans
from ..consts import BIG_REP_FACTOR, MODICUM_TIME
from ..da import extract_testcases, mk_loader, polyclass_matrix
from ._base import BASE_CASES, HasChan


async def xform(it: AsyncIterator[int]) -> AsyncIterator[int]:
    async for n in it:
        yield n + 1


class TransBaseSetup:
    class SetupChan(IsolatedAsyncioTestCase, HasChan):
        async def asyncSetUp(self) -> None:
            self.p = chan(int)
            self.ch = await trans(xform, ch=self.p)


class UpstreamSend(TransBaseSetup.SetupChan):
    async def test_1(self) -> None:
        await (self.p << 1)
        await ([] << self.ch)
        await (self.p << 1)
        await ([] << self.ch)
        await (self.p << 1)
        await sleep(0)
        self.assertEqual(len(self.ch), 1)

    async def test_2(self) -> None:
        fut = gather([] << self.ch, [] << self.ch)
        await (self.p << 1)
        await (self.p << 1)
        await fut
        self.assertEqual(len(self.ch), 0)

    async def test_3(self) -> None:
        sends = islice(iter(lambda: self.p << 1, None), BIG_REP_FACTOR)
        recvs = islice(iter(lambda: [] << self.ch, None), BIG_REP_FACTOR)
        cos: MutableSequence[Awaitable[Any]] = [*sends, *recvs]
        shuffle(cos)
        await wait_for(gather(*cos), timeout=MODICUM_TIME)
        self.assertEqual(len(self.p), 0)
        self.assertEqual(len(self.ch), 0)


TEST_MATRIX = polyclass_matrix(extract_testcases(TransBaseSetup), BASE_CASES)
load_tests = mk_loader(*TEST_MATRIX)

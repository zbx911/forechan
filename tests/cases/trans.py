from asyncio import gather, wait_for
from asyncio.tasks import gather
from itertools import repeat
from random import shuffle
from typing import Any, AsyncIterator, Awaitable, MutableSequence
from unittest import IsolatedAsyncioTestCase

from ...forechan.chan import mk_chan
from ...forechan.trans import trans
from ..consts import MODICUM_TIME, REPEAT_FACTOR
from ..da import extract_testcases, mk_loader, polyclass_matrix
from ._base import BASE_CASES, HasChannel


async def xform(it: AsyncIterator[int]) -> AsyncIterator[int]:
    async for n in it:
        yield n + 1


class TransBaseSetup:
    class SetupChan(IsolatedAsyncioTestCase, HasChannel):
        def setUp(self) -> None:
            self.p = mk_chan(int)
            self.ch = trans(xform, chan=self.p)


class UpstreamSend(TransBaseSetup.SetupChan):
    async def test_1(self) -> None:
        await self.p.send(1)
        await gather(self.ch.recv(), self.p.send(1))

    async def test_2(self) -> None:
        await self.p.send(1)
        await self.ch.recv()
        await self.p.send(1)
        await self.ch.recv()

    async def test_3(self) -> None:
        sends = repeat(self.p.send(1), REPEAT_FACTOR)
        recvs = repeat(self.ch.recv(), REPEAT_FACTOR)
        cos: MutableSequence[Awaitable[Any]] = [*sends, *recvs]
        shuffle(cos)
        await wait_for(gather(*cos), timeout=MODICUM_TIME)
        self.assertEqual(len(self.ch), 0)


TEST_MATRIX = polyclass_matrix(extract_testcases(TransBaseSetup), BASE_CASES)
load_tests = mk_loader(*TEST_MATRIX)

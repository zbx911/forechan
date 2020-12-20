from asyncio import sleep
from asyncio.tasks import gather
from itertools import islice
from random import shuffle
from typing import Any, Awaitable, MutableSequence, Tuple
from unittest import IsolatedAsyncioTestCase

from ...forechan._sched import go
from ...forechan.chan import chan
from ...forechan.select import select
from ...forechan.types import Chan
from ..consts import BIG_REP_FACTOR, MODICUM_TIME
from ..da import extract_testcases, mk_loader, polyclass_matrix
from ._base import BASE_CASES, HasChan


async def delayed_send(ch: Chan[int], n: int, delay: float) -> None:
    async def cont() -> None:
        await sleep(delay)
        await (ch << n)

    await go(cont())


class SelectSetup:
    class SetupChan(IsolatedAsyncioTestCase, HasChan[Tuple[Chan[Any], Any]]):
        async def asyncSetUp(self) -> None:
            self.u1, self.u2 = chan(int), chan(int)
            self.ch = await select(self.u1, self.u2)


class UpstreamSend(SelectSetup.SetupChan):
    async def test_1(self) -> None:
        await (self.u1 << 1)
        c1, r1 = await ([] << self.ch)
        await (self.u2 << 2)
        c2, r2 = await ([] << self.ch)

        self.assertNotEqual(self.u1, self.u2)
        self.assertEqual(c1, self.u1)
        self.assertEqual(r1, 1)
        self.assertEqual(c2, self.u2)
        self.assertEqual(r2, 2)


TEST_MATRIX = polyclass_matrix(extract_testcases(SelectSetup), BASE_CASES)
load_tests = mk_loader(*TEST_MATRIX)

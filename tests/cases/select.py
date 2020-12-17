from asyncio import gather, sleep, wait_for
from asyncio.tasks import create_task, gather
from itertools import islice
from random import shuffle
from typing import Any, Awaitable, MutableSequence
from unittest import IsolatedAsyncioTestCase

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

    create_task(cont())


class SelectBaseSetup:
    class SetupChan(IsolatedAsyncioTestCase, HasChan):
        async def asyncSetUp(self) -> None:
            self.u1, self.u2 = chan(int), chan(int)
            self.ch = await select(self.u1, self.u2)


class UpstreamSend(SelectBaseSetup.SetupChan):
    async def test_1(self) -> None:
        await (self.u2 << 1)
        await (self.u1 << 2)
        r1 = await ([] << self.ch)
        r2 = await ([] << self.ch)
        self.assertEqual(r1, 1)
        self.assertEqual(r2, 2)


TEST_MATRIX = polyclass_matrix(extract_testcases(SelectBaseSetup), BASE_CASES)
load_tests = mk_loader(*TEST_MATRIX)

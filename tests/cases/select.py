from asyncio import sleep
from asyncio.tasks import create_task
from typing import Any, Tuple
from unittest import IsolatedAsyncioTestCase

from ...forechan.chan import chan
from ...forechan.select import select
from ...forechan.types import Chan
from ..da import extract_testcases, mk_loader, polyclass_matrix
from ._base import BASE_CASES


def delayed_send(ch: Chan[int], n: int, delay: float) -> None:
    async def cont() -> None:
        await sleep(delay)
        await (ch << n)

    create_task(cont())


class SelectSetup:
    class SetupChan(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.u1, self.u2 = chan(int), chan(int)
            self.it = select(self.u1, self.u2)


class UpstreamSend(SelectSetup.SetupChan):
    async def test_1(self) -> None:
        await (self.u1 << 1)
        c1, r1 = await self.it.__anext__()
        await (self.u2 << 2)
        c2, r2 = await self.it.__anext__()

        self.assertNotEqual(self.u1, self.u2)
        self.assertEqual(c1, self.u1)
        self.assertEqual(r1, 1)
        self.assertEqual(c2, self.u2)
        self.assertEqual(r2, 2)


TEST_MATRIX = polyclass_matrix(extract_testcases(SelectSetup), BASE_CASES)
load_tests = mk_loader(*TEST_MATRIX)

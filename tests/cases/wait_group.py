from asyncio import TimeoutError, wait_for
from asyncio.tasks import create_task, gather
from unittest import IsolatedAsyncioTestCase

from ...forechan.wait_group import wait_group
from ..consts import SMOL_TIME


class Setup:
    class WG(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.wg = wait_group()


class WaitGroup(Setup.WG):
    async def test_1(self) -> None:
        await wait_for(self.wg.wait(), timeout=SMOL_TIME)

    async def test_2(self) -> None:
        await wait_for(gather(self.wg.wait(), self.wg.wait()), timeout=SMOL_TIME)

    async def test_3(self) -> None:
        self.wg.__enter__()
        self.wg.__exit__(None, None, None)
        with self.assertRaises(ValueError):
            self.wg.__exit__(None, None, None)

    async def test_4(self) -> None:
        with self.wg:
            with self.assertRaises(TimeoutError):
                await wait_for(self.wg.wait(), timeout=SMOL_TIME)

    async def test_5(self) -> None:
        i = 5
        for _ in range(i):

            async def cont() -> None:
                nonlocal i
                with self.wg:
                    i -= 1

            create_task(cont())

        await self.wg.wait()
        self.assertEqual(i, 0)

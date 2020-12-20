from asyncio import sleep
from unittest import IsolatedAsyncioTestCase

from ...forechan.go import go
from ...forechan.chan import chan
from ...forechan.selector import selector
from ...forechan.types import Chan
from ...forechan.wait_group import wait_group


async def delayed_send(ch: Chan[int], n: int, delay: float) -> None:
    async def cont() -> None:
        await sleep(delay)
        await (ch << n)

    await go(cont())


class SelectorSetup:
    class SetupChan(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.wg = wait_group()
            self.u1, self.u2 = chan(int), chan(int)
            self.se = await selector()


class UpstreamSend(SelectorSetup.SetupChan):
    async def test_1(self) -> None:
        await (self.u1 << 1)
        await (self.u2 << 2)

        async with self.se as se:

            @se.on_recvable(ch=self.u1)
            def c1(val: int) -> None:
                with self.wg:
                    self.assertEqual(val, 1)

            @se.on_recvable(ch=self.u2)
            def c2(val: int) -> None:
                with self.wg:
                    self.assertEqual(val, 2)

            async def c0() -> None:
                await self.wg.wait()
                se.close()

            await go(c0)

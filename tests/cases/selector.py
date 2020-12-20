from asyncio import sleep
from unittest import IsolatedAsyncioTestCase

from ...forechan.go import go
from ...forechan.chan import chan
from ...forechan.selector import selector
from ...forechan.types import Chan


async def delayed_send(ch: Chan[int], n: int, delay: float) -> None:
    async def cont() -> None:
        await sleep(delay)
        await (ch << n)

    await go(cont())


class SelectSetup:
    class SetupChan(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.u1, self.u2 = chan(int), chan(int)
            self.se = await selector()


class UpstreamSend(SelectSetup.SetupChan):
    async def test_1(self) -> None:
        await (self.u1 << 1)
        await (self.u2 << 2)

        async with self.se as se:

            @se.on_recvable(ch=self.u1)
            def c1(val: int) -> None:
                self.assertEqual(val, 1)

            @se.on_recvable(ch=self.u2)
            def c2(val: int) -> None:
                self.assertEqual(val, 2)

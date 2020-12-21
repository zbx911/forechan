from asyncio import sleep
from unittest import IsolatedAsyncioTestCase

from ...forechan.chan import chan
from ...forechan.go import go
from ...forechan.selector import selector
from ...forechan.types import Chan


async def delayed_send(ch: Chan[int], n: int, delay: float) -> None:
    async def cont() -> None:
        await sleep(delay)
        await (ch << n)

    await go(cont())


class SelectorSetup:
    class SetupChan(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.u1, self.u2 = chan(int), chan(int)


class UpstreamSend(SelectorSetup.SetupChan):
    async def test_1(self) -> None:
        await (self.u1 << 1)
        await (self.u2 << 2)

        async with await selector() as sr:

            @sr.on_recvable(self.u1)
            def c1(val: int) -> None:
                self.assertEqual(val, 1)
                sr.close()

            @sr.on_recvable(self.u2)
            def c2(val: int) -> None:
                self.assertEqual(val, 2)
                sr.close()

        self.assertFalse(sr)
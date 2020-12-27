from asyncio import sleep
from unittest import IsolatedAsyncioTestCase

from ...forechan.chan import chan
from ...forechan.selector import StopSelector, selector


class SelectorSetup:
    class SetupChan(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.u1, self.u2 = chan(int), chan(int)


class UpstreamSend(SelectorSetup.SetupChan):
    async def test_1(self) -> None:
        await (self.u1 << 1)
        await (self.u2 << 2)

        async with selector() as sr:

            @sr.on_recvable(self.u1)
            def c1(val: int) -> None:
                self.assertEqual(val, 1)
                raise StopSelector()

            @sr.on_recvable(self.u2)
            def c2(val: int) -> None:
                self.assertEqual(val, 2)
                raise StopSelector()

        self.assertFalse(sr)
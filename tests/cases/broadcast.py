from unittest import IsolatedAsyncioTestCase

from ...forechan.broadcast import broadcast
from ..consts import SMOL_REP_FACTOR


class Setup:
    class Chan(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.ch = broadcast(int)


class Broadcast(Setup.Chan):
    async def test_1(self) -> None:
        for _ in range(SMOL_REP_FACTOR):
            await (self.ch << 1)

    async def test_2(self) -> None:
        await (self.ch << 1)
        await (self.ch << 2)
        for _ in range(SMOL_REP_FACTOR):
            cur = await ([] << self.ch)
            self.assertEqual(cur, 2)

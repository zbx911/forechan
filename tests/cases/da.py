from asyncio import sleep
from itertools import islice
from unittest import IsolatedAsyncioTestCase

from ...forechan._da import race
from ..consts import SMOL_REP_FACTOR


class Race(IsolatedAsyncioTestCase):
    async def test_1(self) -> None:
        for i in range(1, SMOL_REP_FACTOR + 1):
            sleeps = islice(iter(lambda: sleep(0, i), None), i)
            ready, pending = await race(*sleeps)
            self.assertEqual(ready, i)
            self.assertEqual(len(pending), i - 1)

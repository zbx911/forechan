from ..forechan.types import Channel
from ..forechan.chan import Chan

from unittest import IsolatedAsyncioTestCase


class BaseSuite(IsolatedAsyncioTestCase):
    async def test_t1(self) -> None:
        ch: Channel = Chan()
        self.assertEqual(True, True)

    async def test_t2(self) -> None:
        self.assertEqual(True, True)

from ..forechan.types import Channel


from unittest import IsolatedAsyncioTestCase
from unittest.case import TestCase


class BaseSuite(IsolatedAsyncioTestCase):
    async def test_t1(self) -> None:
        self.assertEqual(True, True)

    async def test_t2(self) -> None:
        self.assertEqual(True, True)


class BaseSuite2(TestCase):
    def test_t2(self) -> None:
        self.assertEqual(True, True)

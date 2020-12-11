# from ..forechan.types import Channel


from unittest import IsolatedAsyncioTestCase
from unittest.case import TestCase


class BaseSuite(IsolatedAsyncioTestCase):
    async def t1(self) -> None:
        self.assertEqual(True, False)


class BaseSuite2(TestCase):
    async def t2(self) -> None:
        self.assertEqual(True, False)

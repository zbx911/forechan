from ..forechan.types import Channel


from unittest import IsolatedAsyncioTestCase


class BaseSuite(IsolatedAsyncioTestCase):
    async def test_t1(self) -> None:
        self.assertEqual(True, True)

    async def test_t2(self) -> None:
        self.assertEqual(True, True)

from typing import Optional
from unittest import IsolatedAsyncioTestCase
from unittest.loader import TestLoader
from unittest.suite import TestSuite

from ..forechan.chan import Chan
from ._base import BASE_CASES, Channel, HasChannel
from ._da import mixin_matrix
from inspect import getmembers


class BaseSetup:
    class SetupChan(IsolatedAsyncioTestCase, HasChannel):
        def setUp(self) -> None:
            self.ch: Channel = Chan()


class Moo(IsolatedAsyncioTestCase):
    async def test(self) -> None:
        self.assertEqual(5, 34)


def load_tests(
    loader: TestLoader, standard_tests: TestSuite, pattern: Optional[str]
) -> None:
    ret = TestSuite()
    ret.addTest(standard_tests)
    for cls in mixin_matrix((BaseSetup.SetupChan,), BASE_CASES):
        suite = loader.loadTestsFromTestCase(cls)
        ret.addTests(suite)
    return ret

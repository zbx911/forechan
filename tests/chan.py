from typing import Optional
from unittest import IsolatedAsyncioTestCase
from unittest.loader import TestLoader
from unittest.suite import TestSuite

from ..forechan.chan import Chan
from ._base import BASE_CASES, Channel, HasChannel
from ._da import mixin_matrix


class BaseSetup:
    class SetupChan(IsolatedAsyncioTestCase, HasChannel):
        def setUp(self) -> None:
            self.ch: Channel = Chan()


def load_tests(
    loader: TestLoader, standard_tests: TestSuite, pattern: Optional[str]
) -> None:
    tests = (cls() for cls in mixin_matrix((BaseSetup.SetupChan,), BASE_CASES))
    suite = TestSuite()
    suite.addTests(tests)
    return suite

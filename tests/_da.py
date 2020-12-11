from itertools import product
from typing import Callable, Iterator, Optional, Type
from unittest.case import TestCase
from unittest.loader import TestLoader
from unittest.suite import TestSuite


def mixin_matrix(*classes: Iterator[Type]) -> Iterator[Type]:

    for bcs in product(*classes):

        class Mixin_Class(*bcs):
            __qualname__ = f"| {' <|> '.join(bc.__qualname__ for bc in bcs)} |"

        yield Mixin_Class


def mk_loader(
    *tests: TestCase,
) -> Callable[[TestLoader, TestSuite, Optional[str]], TestSuite]:
    def load_tests(
        loader: TestLoader, standard_tests: TestSuite, pattern: Optional[str]
    ) -> None:
        ret = TestSuite()
        ret.addTest(standard_tests)
        for cls in tests:
            suite = loader.loadTestsFromTestCase(cls)
            ret.addTests(suite)
        return ret

    return load_tests

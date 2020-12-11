from itertools import product
from typing import Callable, Iterable, Iterator, Optional, Type
from unittest.case import TestCase
from unittest.loader import TestLoader
from unittest.suite import TestSuite


def polyclass_matrix(*classes: Iterable[Type]) -> Iterator[Type]:

    for bcs in product(*classes):

        class PolyClass(*bcs):
            __qualname__ = f"| {' <|> '.join(bc.__qualname__ for bc in bcs)} |"

        yield PolyClass


def mk_loader(
    *tests: Type[TestCase],
) -> Callable[[TestLoader, TestSuite, Optional[str]], TestSuite]:
    def load_tests(
        loader: TestLoader, standard_tests: TestSuite, pattern: Optional[str]
    ) -> TestSuite:
        ret = TestSuite()
        ret.addTest(standard_tests)
        for cls in tests:
            suite = loader.loadTestsFromTestCase(cls)
            ret.addTests(suite)
        return ret

    return load_tests

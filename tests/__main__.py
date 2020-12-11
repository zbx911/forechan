from os.path import dirname, realpath
from unittest import TestSuite
from unittest.loader import TestLoader
from unittest.result import TestResult

from .base import BaseSuite

SUITE = (BaseSuite(),)

_base_ = dirname(realpath(__file__))


def main() -> None:
    print(_base_)
    loader = TestLoader()
    suite = loader.discover(_base_, pattern="*.py")
    print(suite)
    ret = TestResult()
    suite.run(ret)
    print(ret)


main()

from os.path import dirname, join, realpath
from unittest.loader import TestLoader
from unittest.runner import TextTestRunner


def main() -> None:
    _base_ = dirname(realpath(__file__))
    _parent_ = dirname(_base_)
    _tests_ = join(_base_, "tests")
    loader = TestLoader()
    suite = loader.discover(_tests_, top_level_dir=_parent_, pattern="*.py")
    runner = TextTestRunner()
    runner.run(suite)


main()

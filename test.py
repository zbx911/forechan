#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from os.path import dirname, join, realpath
from unittest.loader import TestLoader
from unittest.runner import TextTestRunner

_base_ = dirname(realpath(__file__))
_parent_ = dirname(_base_)
_tests_ = join(_base_, "tests", "cases")


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbosity", action="count", default=1)
    parser.add_argument("-p", "--pattern", default="*.py")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    loader = TestLoader()
    suite = loader.discover(_tests_, top_level_dir=_parent_, pattern=args.pattern)
    runner = TextTestRunner(verbosity=args.verbosity)
    runner.run(suite)


main()

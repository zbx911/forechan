#!/usr/bin/env python3

from functools import partial
from os import chdir, sep, walk
from os.path import dirname, join, realpath, relpath, splitext
from subprocess import PIPE, run
from typing import Iterator, Mapping, Set, Tuple

_dir_ = dirname(realpath(__file__))
chdir(_dir_)


def ancestors(path: str) -> Iterator[str]:
    if not path:
        return
    parent = dirname(path)
    if path == parent:
        return
    else:
        yield from ancestors(parent)
        yield parent


def git_ls() -> Mapping[str, str]:
    proc = run(
        ("git", "status", "--ignored", "--renames", "--porcelain", "-z"),
        stdout=PIPE,
        text=True,
    )
    proc.check_returncode()
    it = iter(proc.stdout.split("\0"))

    def cont() -> Iterator[Tuple[str, str]]:
        for line in it:
            prefix, file = line[:2], line[3:]
            yield prefix, file.rstrip(sep)
            if "R" in prefix:
                next(it, None)

    entries = {file: prefix for prefix, file in cont()}
    return entries


def git_ignored() -> Iterator[str]:
    for path, stat in git_ls().items():
        if "!" in stat:
            yield path


def tracked_files(search_set: Iterator[str]) -> Iterator[str]:
    ignored = {*git_ignored(), ".git"}
    for path in search_set:
        for parent in ancestors(path):
            if parent in ignored:
                break
        else:
            yield path


def filter_exts(search_set: Iterator[str], exts: Set[str]) -> Iterator[str]:
    for name in search_set:
        _, ext = splitext(name)
        if ext in exts:
            yield name


def ls(base: str) -> Iterator[str]:
    for root, _, files in walk(base):
        prefix = relpath(root, start=base)
        for fn in files:
            yield join(prefix, fn)


def main() -> None:
    search_set = ls(_dir_)
    tracked = tracked_files(search_set)
    py_files = filter_exts(tracked, exts={".py"})
    abs_paths = map(partial(join, _dir_), py_files)
    proc = run(("mypy", "--", *abs_paths))
    exit(proc.returncode)


main()

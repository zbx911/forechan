#!/usr/bin/env python3

from os import sep, walk
from os.path import dirname, join, realpath, splitext
from subprocess import PIPE, run
from typing import Iterator, Mapping, Set, Tuple

_dir_ = dirname(realpath(__file__))


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
        cwd=_dir_,
    )
    proc.check_returncode()
    it = iter(proc.stdout.split("\0"))

    def cont() -> Iterator[Tuple[str, str]]:
        for line in it:
            prefix, file = line[:2], line[3:]
            yield prefix, file.rstrip(sep)
            if "R" in prefix:
                next(it, None)

    entries = {join(_dir_, file): prefix for prefix, file in cont()}
    return entries


def git_ignored() -> Iterator[str]:
    for path, stat in git_ls().items():
        if "!" in stat:
            yield path


def ls(base: str = _dir_) -> Iterator[str]:
    for root, _, files in walk(base):
        for fn in files:
            yield join(root, fn)


def tracked_files() -> Iterator[str]:
    ignored = {*git_ignored(), join(_dir_, ".git")}
    for path in ls():
        for parent in ancestors(path):
            if parent in ignored:
                break
        else:
            yield path


def tracked_files_with_exts(exts: Set[str]) -> Iterator[str]:
    for name in tracked_files():
        _, ext = splitext(name)
        if ext in exts:
            yield name


def main() -> None:
    py_files = tracked_files_with_exts({".py"})
    proc = run(("mypy", "--", *py_files), cwd=_dir_)
    exit(proc.returncode)


main()

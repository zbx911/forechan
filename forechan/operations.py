from itertools import chain
from typing import Any, TypeVar

from .types import Chan

T = TypeVar("T")


def close(ch: Chan[Any], *chs: Chan[Any], close: bool) -> None:
    if close:
        for c in chain((ch,), chs):
            c.close()

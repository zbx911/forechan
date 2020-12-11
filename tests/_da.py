from itertools import product
from typing import Iterator, Type


def mixin_matrix(*classes: Iterator[Type]) -> Iterator[Type]:

    for bcs in product(*classes):

        class Mixin_Class(*bcs):
            __qualname__ = f"| {' <|> '.join(bc.__qualname__ for bc in bcs)} |"

        yield Mixin_Class

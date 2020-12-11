from .types import Channel

from typing import Any, Tuple


def select(*chans: Channel[Any]) -> Channel[Tuple[Channel[Any], Any]]:
    pass

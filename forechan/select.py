from .types import Channel

from typing import Any


def select(*chans: Channel[Any]) -> Channel[Channel[Any], Any]:
    pass

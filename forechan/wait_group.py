from .types import WaitGroup


class _WaitGroup(WaitGroup):
    def __init__(self) -> None:
        self._counter = 0
        self._fut = None

    def __len__(self) -> int:
        return self._counter

    async def wait(self) -> None:
        return None


def wait_group() -> WaitGroup:
    return _WaitGroup()

from typing import Any, AsyncIterator, TypeVar

from .types import Channel, ChannelClosed

T = TypeVar("T")


class BaseChan(Channel[T]):
    async def __aenter__(self) -> Channel[T]:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        try:
            return await self.recv()
        except ChannelClosed:
            raise StopAsyncIteration()

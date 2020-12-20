from abc import abstractmethod
from typing import Protocol

from forechan.types import Chan


class Context(Protocol):
    @property
    @abstractmethod
    def cancelled(self) -> Chan[None]:
        """
        a `broadcast` chan of cancellation signifier
        """

    @property
    @abstractmethod
    def ttl(self) -> float:
        """
        how many seconds until scheduled cancellation
        can be `inf`
        """

    @abstractmethod
    def _cancel() -> None:
        """
        turn on `cancelled` chan
        """
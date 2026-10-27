from abc import ABC, abstractmethod
from typing import Iterator, Any


class BaseProvider(ABC):

    @abstractmethod
    def fetch(self, identifier: str) -> Iterator[Any]:
        """
        Stream records one by one.
        """
        pass
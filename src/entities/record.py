from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class EntityRecord:
    """
    Standard record exchanged between providers and the entity pipeline.
    """

    data: dict[str, Any]

    def get(self, key: str, default=None):
        return self.data.get(key, default)
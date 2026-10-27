from pathlib import Path

from .base import BaseProvider
from entities.record import EntityRecord


class LocalFileProvider(BaseProvider):

    def fetch(self, source):

        filepath = Path(source.identifier)

        if not filepath.exists():
            raise FileNotFoundError(
                f"Entity file not found: {filepath}"
            )

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                entity = line.strip()

                if not entity:
                    continue

                yield EntityRecord({
                    "name": entity
                })
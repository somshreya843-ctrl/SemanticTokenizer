import requests

from .base import BaseProvider
from entities.record import EntityRecord


class OpenLibraryProvider(BaseProvider):

    DATASETS = {
        "books": {
            "url": "https://openlibrary.org/search.json?q=the&limit=100000",
            "format": "json",
        },

        "authors": {
            "url": "https://openlibrary.org/search/authors.json?q=a&limit=100000",
            "format": "json",
        },
    }

    def fetch(self, source):

        identifier = source.identifier

        if identifier not in self.DATASETS:
            raise ValueError(f"Unknown OpenLibrary dataset: {identifier}")

        dataset = self.DATASETS[identifier]

        response = requests.get(dataset["url"])
        response.raise_for_status()

        data = response.json()

        if identifier == "books":

            for row in data.get("docs", []):

                title = row.get("title")

                if not title:
                    continue

                yield EntityRecord({"name": title.strip()})

        elif identifier == "authors":

            for row in data.get("docs", []):

                name = row.get("name")

                if not name:
                    continue

                yield EntityRecord({"name": name.strip()})

        else:
            raise ValueError(f"Unsupported identifier: {identifier}")
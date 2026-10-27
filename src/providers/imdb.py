import gzip
import csv
import requests

from .base import BaseProvider
from entities.record import EntityRecord
from cache.cache_manager import CacheManager


class IMDbProvider(BaseProvider):

    DATASETS = {
        "movies": {
            "url": "https://datasets.imdbws.com/title.basics.tsv.gz",
            "cache": "title.basics",
            "format": "tsv.gz",
        },

        "actors": {
            "url": "https://datasets.imdbws.com/name.basics.tsv.gz",
            "cache": "name.basics",
            "format": "tsv.gz",
        },

        "directors": {
            "url": "https://datasets.imdbws.com/name.basics.tsv.gz",
            "cache": "name.basics",
            "format": "tsv.gz",
        },

        "writers": {
            "url": "https://datasets.imdbws.com/name.basics.tsv.gz",
            "cache": "name.basics",
            "format": "tsv.gz",
        },

        "producers": {
            "url": "https://datasets.imdbws.com/name.basics.tsv.gz",
            "cache": "name.basics",
            "format": "tsv.gz",
        },

        "composers": {
            "url": "https://datasets.imdbws.com/name.basics.tsv.gz",
            "cache": "name.basics",
            "format": "tsv.gz",
        },

        "cinematographers": {
            "url": "https://datasets.imdbws.com/name.basics.tsv.gz",
            "cache": "name.basics",
            "format": "tsv.gz",
        },

        "editors": {
            "url": "https://datasets.imdbws.com/name.basics.tsv.gz",
            "cache": "name.basics",
            "format": "tsv.gz",
        },
    }

    def fetch(self, source):

        identifier = source.identifier

        if identifier not in self.DATASETS:
            raise ValueError(f"Unknown IMDb dataset: {identifier}")

        dataset = self.DATASETS[identifier]

        cache = CacheManager()

        gz_path = cache.get_path(
            provider="imdb",
            identifier=dataset["cache"],
            extension="tsv.gz",
        )

        if not gz_path.exists():

            response = requests.get(dataset["url"], stream=True)
            response.raise_for_status()

            with open(gz_path, "wb") as f:

                for chunk in response.iter_content(chunk_size=1024 * 1024):

                    if chunk:
                        f.write(chunk)

        with gzip.open(gz_path, "rt", encoding="utf-8") as f:

            reader = csv.DictReader(
                f,
                delimiter="\t",
            )

            if identifier == "movies":

                for row in reader:

                    if row["titleType"] != "movie":
                        continue

                    title = row["primaryTitle"].strip()

                    if not title or title == "\\N":
                        continue

                    yield EntityRecord({"name": title})

            else:

                profession_map = {
                    "actors": None,
                    "directors": "director",
                    "writers": "writer",
                    "producers": "producer",
                    "composers": "composer",
                    "cinematographers": "cinematographer",
                    "editors": "editor",
                }

                required = profession_map[identifier]

                for row in reader:

                    name = row["primaryName"].strip()

                    if not name or name == "\\N":
                        continue

                    if required is not None:

                        professions = row["primaryProfession"]

                        if professions == "\\N":
                            continue

                        if required not in professions:
                            continue

                    yield EntityRecord({"name": name})
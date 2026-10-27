import csv
import io
import zipfile
import requests

from .base import BaseProvider
from entities.record import EntityRecord
from cache.cache_manager import CacheManager


class GeoNamesProvider(BaseProvider):

    BASE_URL = "https://download.geonames.org/export/dump"

    def fetch(self, source):

        identifier = source.identifier

        url = f"{self.BASE_URL}/{identifier}.zip"

        cache = CacheManager()

        zip_path = cache.get_path(
            provider="geonames",
            identifier=identifier,
            extension="zip",
        )

        # Download only if not already cached
        if not zip_path.exists():

            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(zip_path, "wb") as f:

                for chunk in response.iter_content(chunk_size=1024 * 1024):

                    if chunk:
                        f.write(chunk)

        # Read directly from cached ZIP
        with zipfile.ZipFile(zip_path) as zf:

            with zf.open(f"{identifier}.txt") as f:

                reader = csv.reader(
                    io.TextIOWrapper(f, encoding="utf-8"),
                    delimiter="\t",
                )

                for row in reader:

                    if source.country_code and row[8] != source.country_code:
                        continue

                    if source.feature_class and row[6] != source.feature_class:
                        continue

                    if source.feature_code and row[7] != source.feature_code:
                        continue

                    yield EntityRecord({
                        "id": row[0],
                        "name": row[1],
                        "ascii_name": row[2],
                        "country_code": row[8],
                        "feature_class": row[6],
                        "feature_code": row[7],
                        "population": row[14],
                    })
import pandas as pd

from entities.record import EntityRecord
from .base import BaseProvider


class GitHubProvider(BaseProvider):

    DATASETS = {
        "iso_countries": {
            "url": "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv",
            "format": "csv",
        },

        "continents": {
            "url": "https://raw.githubusercontent.com/dbouquin/IS_608/master/NanosatDB_munging/Countries-Continents.csv",
            "format": "csv",
        },
    }

    def fetch(self, source):

        identifier = source.identifier

        print(identifier, type(identifier))   # <-- temporary debugging

        if identifier not in self.DATASETS:
            raise ValueError(f"Unknown GitHub dataset: {identifier}")

        dataset = self.DATASETS[identifier]

        if dataset["format"] == "csv":

            df = pd.read_csv(dataset["url"])

            if identifier == "continents":

                values = df["Continent"].dropna().unique()

                for value in values:
                    yield EntityRecord({"name": value})

            else:

                for row in df.to_dict(orient="records"):
                    yield EntityRecord(row)

            return

        raise ValueError(f"Unsupported format: {dataset['format']}")
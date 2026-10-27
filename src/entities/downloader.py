import pandas as pd
import requests


class EntityDownloader:

    def download(self, source):

        if source.source_type == "csv":
            return pd.read_csv(source.url)

        elif source.source_type == "json":

            response = requests.get(source.url)
            response.raise_for_status()

            data = response.json()

            return pd.DataFrame(data)

        elif source.source_type == "html":

            tables = pd.read_html(source.url)

            if len(tables) == 0:
                raise ValueError(f"No HTML tables found at {source.url}")

            return tables[0]

        elif source.source_type == "txt":

            response = requests.get(source.url)
            response.raise_for_status()

            lines = response.text.splitlines()

            return pd.DataFrame({"value": lines})

        else:

            raise ValueError(
                f"Unsupported source type: {source.source_type}"
            )
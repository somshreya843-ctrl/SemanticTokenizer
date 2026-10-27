import io
import zipfile

import pandas as pd
import requests

from .base import BaseProvider
from entities.record import EntityRecord


FAO_URL = "https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data.zip"


class FAOProvider(BaseProvider):

    def fetch(self, source):

        response = requests.get(
            FAO_URL,
            headers={
                "User-Agent": "SemanticTokenizer/1.0"
            },
            timeout=300,
        )
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:

            with z.open("Production_Crops_Livestock_E_ItemCodes.csv") as f:

                df = pd.read_csv(f)

        names = (
            df["Item"]
            .dropna()
            .astype(str)
            .str.strip()
            .drop_duplicates()
            .sort_values()
        )

        for name in names:
            yield EntityRecord(
                {
                    "name": name
                }
            )
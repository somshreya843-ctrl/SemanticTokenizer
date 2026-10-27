from pathlib import Path
import requests

from .base import BaseProvider
from entities.record import EntityRecord


class DictionaryProvider(BaseProvider):

    SOURCE_URL = (
        "https://raw.githubusercontent.com/"
        "dwyl/english-words/refs/heads/master/words_alpha.txt"
    )

    DEFAULT_PATH = Path("data/dictionary/english.txt")

    def fetch(self, source):

        dictionary_path = Path(source.identifier)

        dictionary_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Download only if the dictionary does not exist
        if not dictionary_path.exists() or dictionary_path.stat().st_size == 0:

            print("Downloading English dictionary...")

            response = requests.get(
                self.SOURCE_URL,
                timeout=300
            )

            response.raise_for_status()

            with open(dictionary_path, "wb") as f:
                f.write(response.content)

            print(
                f"Dictionary downloaded from: {self.SOURCE_URL}"
            )

        # Read dictionary
        with open(
            dictionary_path,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                word = line.strip()

                if not word:
                    continue

                # Only alphabetic English words
                if not word.isalpha():
                    continue

                yield EntityRecord({
                    "name": word
                })
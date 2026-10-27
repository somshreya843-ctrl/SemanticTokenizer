import json
import requests
import time

from .base import BaseProvider
from entities.record import EntityRecord
from cache.cache_manager import CacheManager


class WikidataProvider(BaseProvider):

    ENDPOINT = "https://query.wikidata.org/sparql"

    QUERIES = {

        "languages": """
        SELECT DISTINCT ?itemLabel WHERE {
        ?item wdt:P31/wdt:P279* wd:Q34770.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
        }
        """,

        "currencies": """
        SELECT DISTINCT ?itemLabel WHERE {
        ?item wdt:P31/wdt:P279* wd:Q8142.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
        }
        """,

        "chemical_elements": """
        SELECT DISTINCT ?itemLabel WHERE {
        ?item wdt:P31/wdt:P279* wd:Q11344.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
        }
        """,

        "programming_languages": """
        SELECT DISTINCT ?item ?itemLabel ?itemAlias ?articleTitle WHERE {
            ?item wdt:P31/wdt:P279* wd:Q9143.

            OPTIONAL {
                ?item rdfs:label ?itemLabel.
                FILTER(LANG(?itemLabel) = "en")
            }

            OPTIONAL {
                ?item skos:altLabel ?itemAlias.
                FILTER(LANG(?itemAlias) = "en")
            }

            OPTIONAL {
                ?article schema:about ?item;
                        schema:isPartOf <https://en.wikipedia.org/>;
                        schema:name ?articleTitle.
            }
        }
        """,

        "software": """
        SELECT DISTINCT ?itemLabel WHERE {
            ?item wdt:P31/wdt:P279* wd:Q7397.
            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        LIMIT 10000
        """,

        "smartphone": """
        SELECT DISTINCT ?itemLabel WHERE {
            {
                ?item wdt:P279* wd:Q22645.
            }
            UNION
            {
                ?item wdt:P31/wdt:P279* wd:Q22645.
            }
            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        LIMIT 10000
        """,

        "diseases": """
        SELECT DISTINCT ?itemLabel WHERE {
            {
                ?item wdt:P31/wdt:P279* wd:Q12136.
            }
            UNION
            {
                ?item wdt:P31/wdt:P279* wd:Q112193867.
            }

            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        """,

       "medicines": """
        SELECT DISTINCT ?itemLabel WHERE {

            {
                ?item wdt:P31/wdt:P279* wd:Q12140.
            }

            UNION

            {
                ?item wdt:P366 wd:Q12140.
            }

            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        """,

        "companies": """
        SELECT DISTINCT ?itemLabel WHERE {
            ?item wdt:P31 wd:Q783794.
            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        LIMIT 10000
        """,

        "compounds": """
        SELECT DISTINCT ?itemLabel WHERE {
            {
                ?item wdt:P31 wd:Q11173.
            }
            UNION
            {
                ?item wdt:P31/wdt:P279 wd:Q11173.
            }
            UNION
            {
                ?item wdt:P31/wdt:P279/wdt:P279 wd:Q11173.
            }
            UNION
            {
                VALUES ?item {
                    wd:Q48318
                }
            }

            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        """,

        "metals": """
        SELECT DISTINCT ?itemLabel WHERE {
        ?item wdt:P31/wdt:P279* wd:Q11426.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
        }
        """,

        "non_metals": """
        SELECT DISTINCT ?itemLabel WHERE {
        ?item wdt:P31/wdt:P279* wd:Q19478619.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
        }
        """,

       "gases": """
        SELECT DISTINCT ?itemLabel WHERE {

            VALUES ?item {
                wd:Q629
                wd:Q556
                wd:Q1133
                wd:Q1119
                wd:Q654
                wd:Q1303
                wd:Q1318372
                wd:Q1237
                wd:Q1287
            }

            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        """,

        "minerals": """
        SELECT DISTINCT ?itemLabel WHERE {
            {
                ?item wdt:P31/wdt:P279* wd:Q7946.
            }
            UNION
            {
                ?item wdt:P31 wd:Q12089225.
            }
            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        """,

        "acids": """
        SELECT DISTINCT ?itemLabel WHERE {
            {
                ?item wdt:P31/wdt:P279* wd:Q11158.
            }
            UNION
            {
                VALUES ?item {
                    wd:Q4118
                }
            }

            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        """,

        "bases": """
        SELECT DISTINCT ?itemLabel WHERE {
        ?item wdt:P31/wdt:P279* wd:Q11193.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
        }
        """,

        "salts": """
        SELECT DISTINCT ?itemLabel WHERE {
        ?item wdt:P31/wdt:P279* wd:Q12370.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
        }
        """,

        "polymers": """
        SELECT DISTINCT ?itemLabel WHERE {
            ?item wdt:P31/wdt:P279* wd:Q99600509.

            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        """,

        "symptoms": """
        SELECT DISTINCT ?itemLabel WHERE {
            {
                ?item wdt:P31/wdt:P279* wd:Q169872.
            }
            UNION
            {
                ?item wdt:P31/wdt:P279* wd:Q130753312.
            }

            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        """,

        "medical_procedures": """
        SELECT DISTINCT ?itemLabel WHERE {
            ?item wdt:P279/wdt:P279* wd:Q796194.
            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        """,

        "diagnostic_tests": """
        SELECT DISTINCT ?itemLabel WHERE {

            {
                ?item wdt:P31/wdt:P279* wd:Q161238.
            }

            UNION

            {
                VALUES ?item {
                    wd:Q161238
                }
            }

            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        """,

        "vaccines": """
        SELECT DISTINCT ?itemLabel WHERE {
        ?item wdt:P31/wdt:P279* wd:Q134808.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
        }
        """,

        "crops": """
        SELECT DISTINCT ?itemLabel WHERE {
        ?item wdt:P31/wdt:P279* wd:Q917284.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
        }
        """,

        "fertilizers": """
        SELECT DISTINCT ?itemLabel WHERE {
        ?item wdt:P31/wdt:P279* wd:Q83323.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
        }
        """,

        "pesticides": """
        SELECT DISTINCT ?itemLabel WHERE {
            {
                ?item wdt:P31/wdt:P279* wd:Q131656.
            }
            UNION
            {
                VALUES ?item {
                    wd:Q407232
                    wd:Q163648
                }
            }

            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        """,

        "herbicides": """
        SELECT DISTINCT ?itemLabel WHERE {
        ?item wdt:P31/wdt:P279* wd:Q178266.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
        }
        """,

        "nutrients": """
        SELECT DISTINCT ?itemLabel WHERE {
        ?item wdt:P31/wdt:P279* wd:Q181394.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
        }
        """,

        "farm_equipment": """
        SELECT DISTINCT ?itemLabel WHERE {
            {
                ?item wdt:P31/wdt:P279* wd:Q16000047.
            }
            UNION
            {
                VALUES ?item {
                    wd:Q39495
                }
            }

            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en".
            }
        }
        """,
    }

    def fetch(self, source):

        identifier = source.identifier

        if identifier not in self.QUERIES:
            raise ValueError(f"Unknown Wikidata dataset: {identifier}")

        cache = CacheManager()

        cache_path = cache.get_path(
            provider="wikidata",
            identifier=identifier,
            extension="json",
        )

        data = None

        # ----------------------------------------------------
        # Try reading cache
        # ----------------------------------------------------
        if cache_path.exists():

            try:

                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

            except Exception as e:

                print("=" * 70)
                print(f"Corrupted cache detected for {identifier}")
                print(type(e).__name__, str(e))
                print("=" * 70)

                cache_path.unlink(missing_ok=True)
                data = None

        # ----------------------------------------------------
        # Download if cache missing or corrupted
        # ----------------------------------------------------
        if data is None:

            for attempt in range(5):

                try:

                    response = requests.get(
                        self.ENDPOINT,
                        params={
                            "query": self.QUERIES[identifier],
                            "format": "json",
                        },
                        headers={
                            "User-Agent": "SemanticTokenizer/1.0"
                        },
                        timeout=300,
                    )

                    response.raise_for_status()

                    try:
                        data = response.json()

                    except Exception as e:

                        print("=" * 70)
                        print(f"Skipping Wikidata dataset: {identifier}")
                        print(f"Reason: Invalid JSON")
                        print(type(e).__name__, str(e))
                        print("=" * 70)

                        data = None
                        wait = 5 * (attempt + 1)

                        print(
                            f"Invalid JSON received. "
                            f"Retrying in {wait} seconds..."
                        )

                        time.sleep(wait)
                        continue

                    # Save cache only after successful JSON parsing
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(data, f)

                    break

                except requests.exceptions.HTTPError as e:

                    status = e.response.status_code

                    if status in (429, 500, 502, 503, 504):

                        wait = 5 * (attempt + 1)

                        print(
                            f"Wikidata server error ({status}). "
                            f"Retrying in {wait} seconds..."
                        )

                        time.sleep(wait)

                        continue

                    raise

            if data is None:

                print("=" * 70)
                print(f"Skipping dataset: {identifier}")
                print("=" * 70)

                return

        # ----------------------------------------------------
        # Parse
        # ----------------------------------------------------
        results = (
            data.get("results", {})
                .get("bindings", [])
        )

        for row in results:

            name = None

            if "itemLabel" in row:
                name = row["itemLabel"]["value"].strip()

            elif "itemAlias" in row:
                name = row["itemAlias"]["value"].strip()

            elif "articleTitle" in row:
                name = row["articleTitle"]["value"].strip()

            if not name:
                continue

            if name.startswith("Q") and name[1:].isdigit():
                continue

            yield EntityRecord({
                "name": name
            })
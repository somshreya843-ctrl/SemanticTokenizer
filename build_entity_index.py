from collections import defaultdict
from pathlib import Path
import json
import re
import time


# ============================================================
# CONFIGURATION
# ============================================================

ENTITY_DIR = Path("data/entities")

OUTPUT_DIR = Path("data/entity_index")
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

INDEX_FILE = OUTPUT_DIR / "entity_index.jsonl"
AMBIGUOUS_FILE = OUTPUT_DIR / "ambiguous_entities.jsonl"
STATS_FILE = OUTPUT_DIR / "statistics.json"


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_entity(text):

    text = text.strip().lower()

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ============================================================
# BUILD INDEX
# ============================================================

def build_index():

    print("=" * 70)
    print("BUILDING ENTITY INDEX")
    print("=" * 70)

    start_time = time.time()

    total_raw_entries = 0
    total_files = 0

    # --------------------------------------------------------
    # Temporary dictionary
    # --------------------------------------------------------

    entity_map = defaultdict(
        lambda: {
            "text": None,
            "sources": set()
        }
    )

    # --------------------------------------------------------
    # Read all entity files
    # --------------------------------------------------------

    for file_path in sorted(
        ENTITY_DIR.rglob("*.txt")
    ):

        total_files += 1

        category = file_path.parent.name
        label = file_path.stem

        print(
            f"Reading: {file_path}"
        )

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            for line in f:

                entity = line.strip()

                if not entity:
                    continue

                total_raw_entries += 1

                normalized = normalize_entity(
                    entity
                )

                entry = entity_map[normalized]

                if entry["text"] is None:
                    entry["text"] = entity

                entry["sources"].add(
                    (
                        label,
                        category,
                        file_path.name
                    )
                )

    # ========================================================
    # WRITE INDEX
    # ========================================================

    print("\nWriting entity index...")

    total_unique = 0
    total_ambiguous = 0

    with open(
        INDEX_FILE,
        "w",
        encoding="utf-8"
    ) as index_file, open(
        AMBIGUOUS_FILE,
        "w",
        encoding="utf-8"
    ) as ambiguous_file:

        for normalized, data in entity_map.items():

            sources = sorted(
                data["sources"]
            )

            record = {
                "text": data["text"],
                "normalized": normalized,
                "sources": [
                    {
                        "label": label,
                        "category": category,
                        "source_file": source_file
                    }
                    for label, category, source_file
                    in sources
                ]
            }

            index_file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

            total_unique += 1

            # ------------------------------------------------
            # Ambiguous entity
            # ------------------------------------------------

            labels = {
                source[0]
                for source in sources
            }

            if len(labels) > 1:

                ambiguous_file.write(
                    json.dumps(
                        record,
                        ensure_ascii=False
                    ) + "\n"
                )

                total_ambiguous += 1

    # ========================================================
    # STATISTICS
    # ========================================================

    elapsed = time.time() - start_time

    statistics = {
        "total_files": total_files,
        "total_raw_entries": total_raw_entries,
        "total_unique_entities": total_unique,
        "total_ambiguous_entities": total_ambiguous,
        "normalization": "lowercase + whitespace normalization",
        "processing_time_seconds": round(
            elapsed,
            2
        )
    }

    with open(
        STATS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            statistics,
            f,
            indent=2
        )

    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print("\n" + "=" * 70)
    print("ENTITY INDEX COMPLETE")
    print("=" * 70)

    print(
        f"Total files              : {total_files}"
    )

    print(
        f"Total raw entries        : {total_raw_entries}"
    )

    print(
        f"Total unique entities    : {total_unique}"
    )

    print(
        f"Ambiguous entities       : {total_ambiguous}"
    )

    print(
        f"Processing time          : {elapsed:.2f} seconds"
    )

    print(
        f"\nIndex saved to           : {INDEX_FILE}"
    )

    print(
        f"Ambiguous entities saved : {AMBIGUOUS_FILE}"
    )

    print(
        f"Statistics saved to      : {STATS_FILE}"
    )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    build_index()
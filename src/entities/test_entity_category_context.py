from pathlib import Path
import json

from src.entities.context_extractor import ContextExtractor


# --------------------------------------------------
# Configuration
# --------------------------------------------------

ENTITY_INDEX_FILE = Path(
    "data/entity_index/entity_index.jsonl"
)

CONTEXT_WINDOW = 2


# --------------------------------------------------
# Test cases
# --------------------------------------------------

TEST_CASES = [
    # Apple
    {
        "text": "I bought a new Apple iPhone yesterday.",
        "entity": "Apple",
    },
    {
        "text": "I ate a fresh red apple after lunch.",
        "entity": "apple",
    },
    {
        "text": "The apple tree is growing in the garden.",
        "entity": "apple",
    },

    # Amazon
    {
        "text": "Amazon released a new cloud computing service.",
        "entity": "Amazon",
    },
    {
        "text": "The Amazon River is one of the largest rivers in the world.",
        "entity": "Amazon",
    },

    # Jordan
    {
        "text": "Jordan is a country in the Middle East.",
        "entity": "Jordan",
    },
    {
        "text": "Jordan is a city in Minnesota.",
        "entity": "Jordan",
    },

    # Python
    {
        "text": "Python is a popular programming language.",
        "entity": "Python",
    },
    {
        "text": "The python is a large snake found in tropical regions.",
        "entity": "python",
    },

    # Gold
    {
        "text": "Gold is a valuable metal used in jewelry.",
        "entity": "Gold",
    },
    {
        "text": "The gold color of the painting was very bright.",
        "entity": "gold",
    },

    # Jaguar
    {
        "text": "The jaguar is a large wild cat.",
        "entity": "jaguar",
    },
    {
        "text": "Jaguar launched a new luxury car.",
        "entity": "Jaguar",
    },

    # Mercury
    {
        "text": "Mercury is the smallest planet in the Solar System.",
        "entity": "Mercury",
    },
    {
        "text": "Mercury is a chemical element and a liquid metal.",
        "entity": "Mercury",
    },

    # Java
    {
        "text": "Java is widely used for software development.",
        "entity": "Java",
    },
]


# --------------------------------------------------
# Load entity index
# --------------------------------------------------

def load_entity_index():

    entity_index = {}

    print("=" * 70)
    print("LOADING ENTITY INDEX")
    print("=" * 70)

    with open(
        ENTITY_INDEX_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            record = json.loads(line)

            normalized = record.get(
                "normalized",
                record.get("text", "").lower()
            )

            entity_index[normalized] = record

    print(
        f"Loaded entities: {len(entity_index):,}"
    )

    return entity_index


# --------------------------------------------------
# Find entity in text
# --------------------------------------------------

def find_entity_span(text, entity):

    start = text.lower().find(
        entity.lower()
    )

    if start == -1:
        return None

    end = start + len(entity)

    return start, end


# --------------------------------------------------
# Get candidate categories
# --------------------------------------------------

def get_candidate_categories(
    entity_index,
    entity
):

    normalized = " ".join(
        entity.lower().split()
    )

    record = entity_index.get(normalized)

    if record is None:
        return []

    categories = set()

    # Possible formats in entity_index
    if "labels" in record:

        labels = record["labels"]

        if isinstance(labels, list):

            for label in labels:
                categories.add(
                    str(label)
                )

    if "sources" in record:

        sources = record["sources"]

        if isinstance(sources, list):

            for source in sources:
                categories.add(
                    str(source)
                )

    if "label" in record:

        categories.add(
            str(record["label"])
        )

    if "category" in record:

        categories.add(
            str(record["category"])
        )

    return sorted(categories)


# --------------------------------------------------
# Main test
# --------------------------------------------------

def main():

    entity_index = load_entity_index()

    extractor = ContextExtractor(
        context_window=CONTEXT_WINDOW
    )

    print("\n")
    print("=" * 70)
    print("AUTOMATIC ENTITY-CATEGORY CONTEXT TEST")
    print("=" * 70)

    for i, test in enumerate(
        TEST_CASES,
        start=1
    ):

        text = test["text"]
        entity = test["entity"]

        print("\n" + "-" * 70)
        print(f"TEST {i}")
        print("-" * 70)

        print(
            f"Sentence : {text}"
        )

        print(
            f"Entity   : {entity}"
        )

        # ------------------------------------------
        # Find entity span
        # ------------------------------------------

        span = find_entity_span(
            text,
            entity
        )

        if span is None:

            print(
                "STATUS   : ENTITY NOT FOUND"
            )

            continue

        start, end = span

        # ------------------------------------------
        # Extract context
        # ------------------------------------------

        context_info = (
            extractor.extract_context(
                text,
                start,
                end
            )
        )

        context = context_info[
            "context"
        ]

        # ------------------------------------------
        # Get candidate categories
        # ------------------------------------------

        categories = get_candidate_categories(
            entity_index,
            entity
        )

        print(
            f"Context  : {context}"
        )

        print(
            f"Candidates: {categories}"
        )

        if not categories:

            print(
                "STATUS   : NO CANDIDATE CATEGORIES FOUND"
            )

            continue

        print(
            "STATUS   : CANDIDATE CATEGORIES FOUND"
        )


# --------------------------------------------------
# Run
# --------------------------------------------------

if __name__ == "__main__":
    main()
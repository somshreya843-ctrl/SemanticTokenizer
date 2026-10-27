from src.lookup_detector import LookupDetector


# ============================================================
# TEST SENTENCES
# ============================================================

TEST_CASES = [
    "I bought a new Apple iPhone yesterday.",
    "I ate a fresh red apple after lunch.",
    "The apple tree is growing in the garden.",

    "Amazon released a new cloud computing service.",
    "The Amazon River is one of the largest rivers in the world.",

    "Jordan is a country in the Middle East.",
    "Jordan is a city in Minnesota.",

    "Python is a popular programming language.",
    "The python is a large snake found in tropical regions.",

    "Gold is a valuable metal used in jewelry.",
    "The gold color of the painting was very bright.",

    "The jaguar is a large wild cat.",
    "Jaguar launched a new luxury car.",

    "Mercury is the smallest planet in the Solar System.",
    "Mercury is a chemical element and a liquid metal.",

    "Java is widely used for software development.",
]


# ============================================================
# DISPLAY DETECTIONS
# ============================================================

def display_detection(detector, text):

    print("\n" + "=" * 80)
    print("INPUT")
    print("=" * 80)

    print(text)

    entities = detector.detect(text)

    print("\nDETECTED ENTITIES")
    print("-" * 80)

    if not entities:

        print("No entities detected.")
        return

    for i, entity in enumerate(
        entities,
        start=1
    ):

        print(
            f"\nEntity {i}"
        )

        print(
            f"Text   : {entity['text']}"
        )

        print(
            f"Span   : "
            f"{entity['start']} - "
            f"{entity['end']}"
        )

        print(
            f"Source : "
            f"{entity.get('source', 'UNKNOWN')}"
        )

        print(
            "Candidates:"
        )

        candidates = entity.get(
            "candidates",
            []
        )

        if not candidates:

            print(
                "  No candidates"
            )

            continue

        for candidate in candidates:

            print(
                f"  "
                f"{candidate.get('label')} "
                f"→ "
                f"{candidate.get('category')} "
                f""
                f"({candidate.get('source_file')})"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("LOOKUP DETECTOR — MULTI CATEGORY TEST")
    print("=" * 80)

    print(
        "\nInitializing LookupDetector..."
    )

    detector = LookupDetector()

    print(
        "\nDetector initialized."
    )

    for text in TEST_CASES:

        display_detection(
            detector,
            text
        )

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
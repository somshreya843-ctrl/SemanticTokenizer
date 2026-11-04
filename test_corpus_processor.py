# Test entity offset correction
import re

test_cases = [
    ("I ate a fresh apple after lunch.", "Apple", 11, 16),
    ("The apple was sweet and juicy.", "apple", 4, 9),
]

print("\n--- Entity Offset Correction Test ---")

for sentence, entity, start, end in test_cases:
    matches = list(
        re.finditer(re.escape(entity), sentence, re.IGNORECASE)
    )

    if not matches:
        print(f"FAIL: {entity} not found")
        continue

    match = min(matches, key=lambda m: abs(m.start() - start))

    print(f"Sentence: {sentence}")
    print(f"Corrected offsets: {match.start()}, {match.end()}")
    print(f"Matched text: {sentence[match.start():match.end()]}")
    print(
        "PASS" if sentence[match.start():match.end()].casefold()
        == entity.casefold() else "FAIL"
    )
    print("-" * 40)
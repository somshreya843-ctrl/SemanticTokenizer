import json


FILE = "data/entity_index/ambiguous_entities.jsonl"

print("=" * 70)
print("AMBIGUOUS ENTITY INSPECTION")
print("=" * 70)

count = 0

with open(
    FILE,
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        record = json.loads(line)

        print("\n" + "-" * 70)

        print(
            f"Entity: {record['text']}"
        )

        print("Sources:")

        for source in record["sources"]:

            print(
                f"  label={source['label']:<25} "
                f"category={source['category']:<20} "
                f"file={source['source_file']}"
            )

        count += 1

        if count >= 100:
            break


print("\n" + "=" * 70)
print(
    f"Displayed {count} ambiguous entities"
)
print("=" * 70)
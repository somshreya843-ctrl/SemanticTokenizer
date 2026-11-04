from src.corpus_processor import CorpusProcessor


ENTITY_FILE = "data/test_cases/entities_75.txt"

processor = CorpusProcessor()


with open(ENTITY_FILE, "r", encoding="utf-8") as f:
    entities = [
        line.strip()
        for line in f
        if line.strip()
    ]


passed = 0
failed = 0


print("=" * 100)
print("75 ENTITY VERIFICATION")
print("=" * 100)


for i, expected_entity in enumerate(entities, start=1):

    test_input = f"{expected_entity} is present."

    output, detected_entities = processor.process_document(
        test_input
    )

    found = False
    matched_entity = None
    matched_label = None

    for entity in detected_entities:

        if entity["text"].casefold() == expected_entity.casefold():

            found = True
            matched_entity = entity["text"]
            matched_label = entity["label"]
            break


    print("\n" + "=" * 100)
    print(f"TEST {i}")
    print(f"EXPECTED : {expected_entity}")
    print(f"INPUT    : {test_input}")
    print(f"OUTPUT   : {output}")

    if found:

        print(f"DETECTED : {matched_entity}")
        print(f"LABEL    : {matched_label}")
        print("STATUS   : ✅ PASSED")

        passed += 1

    else:

        print("DETECTED : NOT FOUND")
        print("STATUS   : ❌ FAILED")

        failed += 1


print("\n" + "=" * 100)
print("VERIFICATION SUMMARY")
print("=" * 100)

print(f"Total Entities : {len(entities)}")
print(f"Passed         : {passed}")
print(f"Failed         : {failed}")

if failed == 0:
    print("\n🎉 ALL 75 ENTITIES PASSED")
else:
    print("\n⚠️ SOME ENTITIES FAILED")

print("=" * 100)
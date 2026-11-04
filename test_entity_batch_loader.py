from src.entities.entity_batch_loader import EntityBatchLoader


loader = EntityBatchLoader(
    entity_dir="data/entities",
    batch_size=1024
)


print("=" * 70)
print("STRUCTURED ENTITY LOADER TEST")
print("=" * 70)


total_entities = 0
total_batches = 0


for batch in loader.iter_batches():

    total_batches += 1
    total_entities += len(batch)

    if total_batches <= 3:

        print(f"\nBatch {total_batches}")
        print(f"Batch size: {len(batch)}")

        print("\nFirst 5 entities:")

        for entity in batch[:5]:

            print(
                f"  {entity['text']} | "
                f"label={entity['label']} | "
                f"category={entity['category']} | "
                f"source={entity['source_file']}"
            )


print("\n" + "=" * 70)
print("LOADER TEST COMPLETE")
print("=" * 70)

print(f"Total raw entries : {total_entities}")
print(f"Total batches     : {total_batches}")
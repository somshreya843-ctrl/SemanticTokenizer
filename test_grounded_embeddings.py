import json

from src.entities.context_embedder import ContextEmbedder
from src.entities.batched_context_embedder import BatchedContextEmbedder


INPUT_FILE = "data/grounded/entity_sentences.jsonl"


# ---------------------------------------------------------
# Load Stage-A grounded records
# ---------------------------------------------------------

records = []

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        line = line.strip()

        if line:
            records.append(
                json.loads(line)
            )


print("=" * 60)
print("STAGE-B EMBEDDING TEST")
print("=" * 60)
print(f"Grounded records : {len(records)}")


# ---------------------------------------------------------
# Initialize embedding model
# ---------------------------------------------------------

context_embedder = ContextEmbedder()


# ---------------------------------------------------------
# Generate embeddings
# ---------------------------------------------------------

embedder = BatchedContextEmbedder(
    context_embedder=context_embedder,
    batch_size=4,
    shard_size=100
)

embedder.process(records)

import torch
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


INPUT_FILE = "data/embeddings/grounded_shards/embeddings_00000.pt"

records = torch.load(
    INPUT_FILE,
    map_location="cpu"
)

print("=" * 60)
print("STAGE-C: ENTITY SENSE CLUSTERING TEST")
print("=" * 60)

# ---------------------------------------------------------
# Group by entity + sentence
# Preserve all candidate types
# ---------------------------------------------------------

groups = defaultdict(dict)

for record in records:

    entity = record["entity"].casefold()
    sentence = record["sentence"]

    key = (entity, sentence)

    if key not in groups[entity]:
        groups[entity][key] = {
            "entity": record["entity"],
            "sentence": sentence,
            "embedding": record["embedding"],
            "types": []
        }

    if record["type"] not in groups[entity][key]["types"]:
        groups[entity][key]["types"].append(
            record["type"]
        )


# ---------------------------------------------------------
# Level-1 semantic sense clustering
# ---------------------------------------------------------

for entity, context_dict in groups.items():

    items = list(context_dict.values())

    X = torch.stack([
        item["embedding"]
        for item in items
    ]).numpy()

    print(f"\nEntity: {entity}")
    print(f"Unique contexts: {len(items)}")

    # -----------------------------------------------------
    # One unique context = one sense
    # -----------------------------------------------------

    if len(items) < 3:

        print("Selected K: 1")
        print("Reason: insufficient unique contexts")

        for item in items:
            print(
                f"  Types: {item['types']}"
            )
            print(
                f"  Sentence: {item['sentence']}"
            )

        continue

    # -----------------------------------------------------
    # Find best K using silhouette score
    # -----------------------------------------------------

    best_k = 1
    best_score = -1.0

    max_k = len(items) - 1

    for k in range(2, max_k + 1):

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )

        labels = model.fit_predict(X)

        if len(set(labels)) < 2:
            continue

        score = silhouette_score(
            X,
            labels
        )

        print(
            f"  K={k} silhouette={score:.4f}"
        )

        if score > best_score:

            best_score = score
            best_k = k

    print(f"Selected K: {best_k}")

    # -----------------------------------------------------
    # Display clusters
    # -----------------------------------------------------

    if best_k > 1:

        model = KMeans(
            n_clusters=best_k,
            random_state=42,
            n_init=10
        )

        labels = model.fit_predict(X)

        for cluster_id in range(best_k):

            cluster_items = [
                items[i]
                for i in range(len(items))
                if labels[i] == cluster_id
            ]

            print(
                f"  Cluster {cluster_id}: "
                f"{len(cluster_items)} contexts"
            )

            for item in cluster_items:

                print(
                    f"    Types: {item['types']}"
                )

                print(
                    f"    Sentence: {item['sentence']}"
                )

print("\n" + "=" * 60)
print("LEVEL-1 CLUSTERING TEST COMPLETE")
print("=" * 60)
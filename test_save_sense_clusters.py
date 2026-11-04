import json
import torch
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


INPUT_FILE = "data/embeddings/grounded_shards/embeddings_00000.pt"
OUTPUT_FILE = "data/clusters/level1_sense_clusters.jsonl"


records = torch.load(
    INPUT_FILE,
    map_location="cpu"
)

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
        groups[entity][key]["types"].append(record["type"])


output = []

for entity, context_dict in groups.items():

    items = list(context_dict.values())

    X = torch.stack([
        item["embedding"]
        for item in items
    ]).numpy()

    # ---------------------------------------------
    # Select K
    # ---------------------------------------------

    best_k = 1
    best_score = -1.0

    if len(items) >= 3:

        max_k = min(3, len(items) - 1)

        for k in range(2, max_k + 1):

            model = KMeans(
                n_clusters=k,
                random_state=42,
                n_init=10
            )

            labels = model.fit_predict(X)

            if len(set(labels)) < 2:
                continue

            score = silhouette_score(X, labels)

            if score > best_score:
                best_score = score
                best_k = k

    # ---------------------------------------------
    # Final clustering
    # ---------------------------------------------

    if best_k == 1:

        labels = [0] * len(items)

        centroid = torch.tensor(
            X.mean(axis=0),
            dtype=torch.float32
        )

        clusters = [{
            "sense_id": 0,
            "centroid": centroid.tolist(),
            "contexts": []
        }]

    else:

        model = KMeans(
            n_clusters=best_k,
            random_state=42,
            n_init=10
        )

        labels = model.fit_predict(X)

        clusters = []

        for cluster_id in range(best_k):

            cluster_indices = [
                i for i, label in enumerate(labels)
                if label == cluster_id
            ]

            centroid = torch.tensor(
                X[cluster_indices].mean(axis=0),
                dtype=torch.float32
            )

            clusters.append({
                "sense_id": cluster_id,
                "centroid": centroid.tolist(),
                "contexts": []
            })

    # ---------------------------------------------
    # Attach contexts
    # ---------------------------------------------

    for i, item in enumerate(items):

        clusters[labels[i]]["contexts"].append({
            "sentence": item["sentence"],
            "types": item["types"]
        })

    output.append({
        "entity": entity,
        "num_senses": best_k,
        "silhouette": (
            None if best_k == 1
            else float(best_score)
        ),
        "senses": clusters
    })


# ---------------------------------------------
# Save
# ---------------------------------------------

import os
os.makedirs(
    "data/clusters",
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    for item in output:
        f.write(
            json.dumps(item)
            + "\n"
        )


print("=" * 60)
print("LEVEL-1 SENSE CLUSTERS SAVED")
print("=" * 60)
print(f"Entities: {len(output)}")
print(f"Output:   {OUTPUT_FILE}")

for item in output:

    print(
        f"{item['entity']}: "
        f"{item['num_senses']} sense(s)"
    )

print("=" * 60)

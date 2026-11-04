import json
import numpy as np
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


INPUT_FILE = "data/clusters/level1_sense_clusters.jsonl"
OUTPUT_FILE = "data/clusters/level2_type_clusters.jsonl"


type_groups = defaultdict(dict)


with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line in f:

        item = json.loads(line)

        for sense in item["senses"]:

            for context in sense["contexts"]:

                for entity_type in context["types"]:

                    key = (
                        item["entity"],
                        sense["sense_id"]
                    )

                    type_groups[entity_type][key] = {
                        "entity": item["entity"],
                        "sense_id": sense["sense_id"],
                        "centroid": sense["centroid"]
                    }


print("=" * 60)
print("LEVEL-2 TYPE CLUSTERING TEST")
print("=" * 60)


output_records = []


for entity_type, senses_dict in sorted(type_groups.items()):

    senses = list(senses_dict.values())

    X = np.array([
        item["centroid"]
        for item in senses
    ])

    print(f"\nType: {entity_type}")
    print(f"Input sense centroids: {len(senses)}")


    # -----------------------------------------------------
    # Not enough centroids for clustering
    # -----------------------------------------------------

    if len(senses) < 3:

        print("Selected K: 1")
        print("Reason: insufficient sense centroids")

        output_records.append({
            "type": entity_type,
            "selected_k": 1,
            "silhouette": None,
            "clusters": [
                {
                    "cluster_id": 0,
                    "members": [
                        {
                            "entity": sense["entity"],
                            "sense_id": sense["sense_id"],
                            "centroid": sense["centroid"]
                        }
                        for sense in senses
                    ]
                }
            ]
        })

        continue


    # -----------------------------------------------------
    # Automatic K selection
    # -----------------------------------------------------

    best_k = 1
    best_score = -1.0

    # No hard-coded maximum K
    max_k = len(senses) - 1


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

        print(
            f"  K={k} silhouette={score:.4f}"
        )

        if score > best_score:

            best_score = score
            best_k = k


    print(f"Selected K: {best_k}")


    # -----------------------------------------------------
    # Final clustering using selected K
    # -----------------------------------------------------

    model = KMeans(
        n_clusters=best_k,
        random_state=42,
        n_init=10
    )

    labels = model.fit_predict(X)


    clusters = []


    for cluster_id in range(best_k):

        cluster_items = []


        for i, sense in enumerate(senses):

            if labels[i] == cluster_id:

                cluster_items.append({
                    "entity": sense["entity"],
                    "sense_id": sense["sense_id"],
                    "centroid": sense["centroid"]
                })


        clusters.append({
            "cluster_id": cluster_id,
            "members": cluster_items
        })


    # -----------------------------------------------------
    # Save result for this type
    # -----------------------------------------------------

    output_records.append({
        "type": entity_type,
        "selected_k": best_k,
        "silhouette": (
            None
            if best_k == 1
            else float(best_score)
        ),
        "clusters": clusters
    })


# ---------------------------------------------------------
# Save all Level-2 results
# ---------------------------------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    for record in output_records:

        f.write(
            json.dumps(record) + "\n"
        )


print(f"\nSaved Level-2 clusters to: {OUTPUT_FILE}")

print("\n" + "=" * 60)
print("LEVEL-2 TYPE CLUSTERING COMPLETE")
print("=" * 60)
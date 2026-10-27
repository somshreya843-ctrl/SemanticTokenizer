import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


class SemanticClustering:

    def __init__(
        self,
        embedding_dir="data/embeddings/grounded_shards",
        output_file="data/clusters/level1_sense_clusters.jsonl",
    ):
        self.embedding_dir = Path(embedding_dir)
        self.output_file = Path(output_file)

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    # =========================================================
    # Load embedding shards
    # =========================================================

    def load_embeddings(self):

        records = []

        shard_files = sorted(
            self.embedding_dir.glob("embeddings_*.pt")
        )

        for shard_file in shard_files:

            shard = torch.load(
                shard_file,
                map_location="cpu"
            )

            records.extend(shard)

        print(f"Loaded embeddings: {len(records)}")

        return records

    # =========================================================
    # Group unique contexts by entity
    # =========================================================

    def group_by_entity(self, records):

        groups = defaultdict(dict)

        for record in records:

            entity = record["entity"].casefold()
            sentence = record["sentence"]

            key = (
                entity,
                sentence
            )

            if key not in groups[entity]:

                groups[entity][key] = {
                    "entity": record["entity"],
                    "sentence": sentence,
                    "embedding": record["embedding"],
                    "types": []
                }

            entity_types = groups[entity][key]["types"]

            if record["type"] not in entity_types:

                entity_types.append(
                    record["type"]
                )

        return groups

    # =========================================================
    # Dynamic K selection
    # =========================================================

    def select_k(self, X):

        n_samples = len(X)

        # Silhouette requires:
        # 2 <= K < number of samples

        if n_samples < 3:

            return 1, None

        best_k = 1
        best_score = -1.0

        max_k = n_samples - 1

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

            if score > best_score:

                best_score = score
                best_k = k

        if best_k == 1:

            return 1, None

        return best_k, float(best_score)

    # =========================================================
    # Cluster one entity
    # =========================================================

    def cluster_entity(self, items):

        X = np.array([
            item["embedding"].numpy()
            if torch.is_tensor(item["embedding"])
            else np.asarray(item["embedding"])
            for item in items
        ])

        selected_k, silhouette = self.select_k(X)

        # -----------------------------------------------------
        # Single sense
        # -----------------------------------------------------

        if selected_k == 1:

            centroid = X.mean(
                axis=0
            )

            return {
                "selected_k": 1,
                "silhouette": None,
                "senses": [
                    {
                        "sense_id": 0,
                        "centroid": centroid.tolist(),
                        "contexts": [
                            {
                                "sentence": item["sentence"],
                                "types": item["types"]
                            }
                            for item in items
                        ]
                    }
                ]
            }

        # -----------------------------------------------------
        # Final KMeans
        # -----------------------------------------------------

        model = KMeans(
            n_clusters=selected_k,
            random_state=42,
            n_init=10
        )

        labels = model.fit_predict(X)

        senses = []

        for cluster_id in range(selected_k):

            indices = [
                i
                for i, label in enumerate(labels)
                if label == cluster_id
            ]

            cluster_vectors = X[indices]

            centroid = cluster_vectors.mean(
                axis=0
            )

            contexts = []

            for index in indices:

                item = items[index]

                contexts.append({
                    "sentence": item["sentence"],
                    "types": item["types"]
                })

            senses.append({
                "sense_id": cluster_id,
                "centroid": centroid.tolist(),
                "contexts": contexts
            })

        return {
            "selected_k": selected_k,
            "silhouette": silhouette,
            "senses": senses
        }

    # =========================================================
    # Level-2: Global unsupervised semantic clustering
    # =========================================================

    def run_level2(
        self,
        level1_file="data/clusters/level1_sense_clusters.jsonl",
        output_file="data/clusters/level2_global_clusters.jsonl"
    ):

        level1_file = Path(level1_file)
        output_file = Path(output_file)

        # -----------------------------------------------------
        # Load all Level-1 sense centroids
        # -----------------------------------------------------

        senses = []

        with open(
            level1_file,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                item = json.loads(line)

                for sense in item["senses"]:
                    candidate_types = sorted({
                        t
                        for context in sense["contexts"]
                        for t in context.get("types", [])
                    })

                    senses.append({
                        "entity": item["entity"],
                        "sense_id": sense["sense_id"],
                        "centroid": sense["centroid"],
                        "candidate_types": candidate_types,
                        "contexts": sense["contexts"]
                    })

        print("=" * 60)
        print("LEVEL-2 GLOBAL UNSUPERVISED CLUSTERING")
        print("=" * 60)

        print(
            f"Input sense centroids: {len(senses)}"
        )

        # -----------------------------------------------------
        # Build global embedding matrix
        # -----------------------------------------------------

        X = np.array([
            sense["centroid"]
            for sense in senses
        ])

        # -----------------------------------------------------
        # Automatic K selection
        # -----------------------------------------------------

        selected_k, silhouette = self.select_k(X)

        print(
            f"Selected K: {selected_k}"
        )

        if silhouette is not None:

            print(
                f"Silhouette: {silhouette:.4f}"
            )

        # -----------------------------------------------------
        # Final global clustering
        # -----------------------------------------------------

        if selected_k == 1:

            labels = np.zeros(
                len(senses),
                dtype=int
            )

        else:

            model = KMeans(
                n_clusters=selected_k,
                random_state=42,
                n_init=10
            )

            labels = model.fit_predict(X)

        # -----------------------------------------------------
        # Build semantic clusters
        # -----------------------------------------------------

        clusters = []

        for cluster_id in range(selected_k):

            members = []

            for index, sense in enumerate(senses):

                if labels[index] != cluster_id:
                    continue

                members.append({
                    "entity": sense["entity"],
                    "sense_id": sense["sense_id"],
                    "candidate_types": sense["candidate_types"],
                    "centroid": sense["centroid"],
                    "contexts": sense["contexts"]
                })

            cluster_centroid = X[
                labels == cluster_id
            ].mean(axis=0)

            clusters.append({
                "cluster_id": cluster_id,
                "centroid": cluster_centroid.tolist(),
                "members": members
            })

        # -----------------------------------------------------
        # Save global semantic clusters
        # -----------------------------------------------------

        output = {
            "level": 2,
            "method": "global_unsupervised_kmeans",
            "input_sense_count": len(senses),
            "selected_k": selected_k,
            "silhouette": silhouette,
            "clusters": clusters
        }

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                output,
                f,
                indent=2
            )

        print(
            f"Output: {output_file}"
        )

        print("=" * 60)
        print("LEVEL-2 GLOBAL CLUSTERING COMPLETE")
        print("=" * 60)
    # =========================================================
    # Level-1 clustering
    # =========================================================

    def run_level1(self):

        records = self.load_embeddings()

        groups = self.group_by_entity(
            records
        )

        print("=" * 60)
        print("LEVEL-1 ENTITY SENSE CLUSTERING")
        print("=" * 60)

        output = []

        for entity in sorted(groups):

            items = list(
                groups[entity].values()
            )

            result = self.cluster_entity(
                items
            )

            output.append({
                "entity": entity,
                **result
            })

            print(
                f"{entity}: "
                f"{result['selected_k']} sense(s)"
            )

        with open(
            self.output_file,
            "w",
            encoding="utf-8"
        ) as f:

            for item in output:

                f.write(
                    json.dumps(item)
                    + "\n"
                )

        print("=" * 60)
        print("LEVEL-1 CLUSTERING COMPLETE")
        print("=" * 60)

        print(
            f"Entities: {len(output)}"
        )

        print(
            f"Output: {self.output_file}"
        )
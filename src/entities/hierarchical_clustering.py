import json
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


class HierarchicalSemanticClustering:

    def __init__(
        self,
        level1_file="data/clusters/level1_sense_clusters.jsonl",
        output_file="data/clusters/semantic_entity_tree.json",
        min_cluster_size=2,
        max_depth=8,
    ):
        self.level1_file = Path(level1_file)
        self.output_file = Path(output_file)

        self.min_cluster_size = min_cluster_size
        self.max_depth = max_depth

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    # ---------------------------------------------------------
    # LOAD LEVEL-1 SENSES
    # ---------------------------------------------------------

    def load_senses(self):

        senses = []

        with open(self.level1_file, "r", encoding="utf-8") as f:

            for line in f:

                entity_data = json.loads(line)

                entity = entity_data["entity"]

                for sense in entity_data["senses"]:

                    candidate_types = sorted({
                        t
                        for context in sense.get("contexts", [])
                        for t in context.get("types", [])
                    })

                    senses.append({
                        "entity": entity,
                        "sense_id": sense["sense_id"],
                        "centroid": sense["centroid"],
                        "candidate_types": candidate_types,
                        "contexts": sense.get("contexts", [])
                    })

        print(f"Loaded senses: {len(senses)}")

        return senses

    # ---------------------------------------------------------
    # SELECT K FOR ONE NODE
    # ---------------------------------------------------------

    def select_k(self, X):

        n = len(X)

        if n < 3:
            return 1

        max_k = min(n - 1, 8)

        best_k = 1
        best_score = -1

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

        return best_k

    # ---------------------------------------------------------
    # RECURSIVE TREE BUILDING
    # ---------------------------------------------------------

    def build_node(
        self,
        members,
        node_id,
        depth
    ):

        node = {
            "node_id": node_id,
            "depth": depth,
            "size": len(members),
            "members": [],
            "children": []
        }

        # Store entities in this node
        for member in members:

            node["members"].append({
                "entity": member["entity"],
                "sense_id": member["sense_id"],
                "candidate_types": member["candidate_types"],
                "contexts": member["contexts"]
            })

        # Stop conditions
        if (
            len(members) < self.min_cluster_size * 2
            or depth >= self.max_depth
        ):
            node["leaf"] = True
            return node

        X = np.array([
            member["centroid"]
            for member in members
        ])

        k = self.select_k(X)

        # Cannot meaningfully split
        if k <= 1 or k >= len(members):
            node["leaf"] = True
            return node

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )

        labels = model.fit_predict(X)

        # Build child branches
        for cluster_id in range(k):

            indices = [
                i
                for i, label in enumerate(labels)
                if label == cluster_id
            ]

            if len(indices) < self.min_cluster_size:
                continue

            child_members = [
                members[i]
                for i in indices
            ]

            child = self.build_node(
                child_members,
                f"{node_id}.{cluster_id}",
                depth + 1
            )

            node["children"].append(child)

        node["leaf"] = len(node["children"]) == 0

        return node

    # ---------------------------------------------------------
    # BUILD COMPLETE TREE
    # ---------------------------------------------------------

    def run(self):

        senses = self.load_senses()

        print("=" * 60)
        print("HIERARCHICAL SEMANTIC CLUSTERING")
        print("=" * 60)

        root = self.build_node(
            senses,
            node_id="root",
            depth=0
        )

        tree = {
            "name": "Semantic Entity Tree",
            "method": "recursive_unsupervised_kmeans",
            "num_senses": len(senses),
            "max_depth": self.max_depth,
            "tree": root
        }

        with open(
            self.output_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                tree,
                f,
                indent=2
            )

        print("=" * 60)
        print("HIERARCHICAL CLUSTERING COMPLETE")
        print(f"Senses: {len(senses)}")
        print(f"Output: {self.output_file}")
        print("=" * 60)


if __name__ == "__main__":

    clustering = HierarchicalSemanticClustering()

    clustering.run()
from collections import defaultdict
from itertools import combinations


class HardNegativeMiner:
    """
    Automatically generates hard-negative candidate pairs.

    Two sources are used:

    1. Same surface form + different labels
       Example:
           Apple + company
           Apple + crop

    2. Similar embeddings + different labels
       Example:
           entity A + type A
           entity B + type B
       where their embeddings are very similar.
    """

    def __init__(
        self,
        similarity_threshold=0.80,
        max_context_negatives_per_entity=5
    ):
        self.similarity_threshold = similarity_threshold
        self.max_context_negatives_per_entity = (
            max_context_negatives_per_entity
        )

    # ---------------------------------------------------------
    # SOURCE 1:
    # Same surface form + different type
    # ---------------------------------------------------------

    def mine_same_surface_negatives(self, entity_type_records):

        grouped = defaultdict(list)

        for index, record in enumerate(entity_type_records):

            normalized = record["normalized"]

            grouped[normalized].append({
                "index": index,
                "text": record["text"],
                "label": record["label"],
                "category": record["category"]
            })

        pairs = []

        for normalized, records in grouped.items():

            if len(records) < 2:
                continue

            for first, second in combinations(records, 2):

                if first["label"] == second["label"]:
                    continue

                pairs.append({
                    "index1": first["index"],
                    "index2": second["index"],
                    "text1": first["text"],
                    "text2": second["text"],
                    "label1": first["label"],
                    "label2": second["label"],
                    "category1": first["category"],
                    "category2": second["category"],
                    "pair_type": "same_surface_different_type"
                })

        return pairs

    # ---------------------------------------------------------
    # SOURCE 2:
    # Similar embedding + different type
    # ---------------------------------------------------------

    def mine_similar_context_negatives(
        self,
        records,
        embeddings
    ):

        import torch
        import torch.nn.functional as F

        embeddings = torch.stack(embeddings)

        embeddings = F.normalize(
            embeddings,
            p=2,
            dim=1
        )

        similarity_matrix = torch.mm(
            embeddings,
            embeddings.T
        )

        pairs = []
        per_entity_count = defaultdict(int)

        number_of_entities = len(records)

        for i in range(number_of_entities):

            if per_entity_count[i] >= self.max_context_negatives_per_entity:
                continue

            similarities = similarity_matrix[i]

            candidates = torch.where(
                similarities >= self.similarity_threshold
            )[0]

            candidates = candidates.tolist()

            candidates.sort(
                key=lambda j: float(similarities[j]),
                reverse=True
            )

            for j in candidates:

                if i == j:
                    continue

                if per_entity_count[i] >= (
                    self.max_context_negatives_per_entity
                ):
                    break

                label_i = records[i]["label"]
                label_j = records[j]["label"]

                if label_i == label_j:
                    continue

                if i > j:
                    continue

                similarity = float(similarities[j])

                pairs.append({
                    "index1": i,
                    "index2": j,
                    "text1": records[i]["text"],
                    "text2": records[j]["text"],
                    "label1": label_i,
                    "label2": label_j,
                    "category1": records[i]["category"],
                    "category2": records[j]["category"],
                    "similarity": similarity,
                    "pair_type": "similar_context_different_type"
                })

                per_entity_count[i] += 1
                per_entity_count[j] += 1

        return pairs

    # ---------------------------------------------------------
    # COMBINE BOTH SOURCES
    # ---------------------------------------------------------

    def mine(
        self,
        records,
        embeddings=None
    ):

        print("=" * 70)
        print("AUTOMATIC HARD-NEGATIVE MINING")
        print("=" * 70)

        print("\nSource 1:")
        print("Same surface + different type")

        same_surface_pairs = (
            self.mine_same_surface_negatives(records)
        )

        print(
            f"Found: {len(same_surface_pairs)} pairs"
        )

        similar_context_pairs = []

        if embeddings is not None:

            print("\nSource 2:")
            print("Similar embedding + different type")

            similar_context_pairs = (
                self.mine_similar_context_negatives(
                    records,
                    embeddings
                )
            )

            print(
                f"Found: {len(similar_context_pairs)} pairs"
            )

        # -----------------------------------------------------
        # Deduplicate
        # -----------------------------------------------------

        all_pairs = (
            same_surface_pairs +
            similar_context_pairs
        )

        unique_pairs = {}

        for pair in all_pairs:

            key = tuple(
                sorted(
                    [
                        pair["index1"],
                        pair["index2"]
                    ]
                )
            )

            if key not in unique_pairs:
                unique_pairs[key] = pair

        final_pairs = list(unique_pairs.values())

        print("\nFinal hard negatives:")
        print(f"Total: {len(final_pairs)}")

        return final_pairs
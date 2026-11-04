import torch
import torch.nn.functional as F


# ============================================================
# LOAD EMBEDDINGS
# ============================================================

original_data = torch.load(
    "data/embeddings/test_embeddings.pt",
    weights_only=False
)

refined_data = torch.load(
    "data/embeddings/refined_embeddings.pt",
    weights_only=False
)


# ============================================================
# FIND SAME-SURFACE-FORM / DIFFERENT-LABEL PAIRS
# ============================================================

from collections import defaultdict
from itertools import combinations


groups = defaultdict(list)

for index, item in enumerate(original_data):

    key = item["text"].strip().lower()

    groups[key].append(index)


print("\n" + "=" * 80)
print("AMBIGUOUS ENTITY VALIDATION")
print("=" * 80)


found = False


for surface, indices in groups.items():

    if len(indices) < 2:
        continue

    for idx1, idx2 in combinations(
        indices,
        2
    ):

        item1 = original_data[idx1]
        item2 = original_data[idx2]

        # Only same text + different labels
        if item1["label"] == item2["label"]:
            continue

        found = True

        original_1 = (
            item1["embedding"]
            .float()
            .unsqueeze(0)
        )

        original_2 = (
            item2["embedding"]
            .float()
            .unsqueeze(0)
        )

        refined_1 = (
            refined_data[idx1]["refined_embedding"]
            .float()
            .unsqueeze(0)
        )

        refined_2 = (
            refined_data[idx2]["refined_embedding"]
            .float()
            .unsqueeze(0)
        )

        similarity_before = (
            F.cosine_similarity(
                original_1,
                original_2
            ).item()
        )

        similarity_after = (
            F.cosine_similarity(
                refined_1,
                refined_2
            ).item()
        )

        print("\n" + "-" * 80)

        print(
            f"Entity 1 : {item1['text']}"
        )

        print(
            f"Label 1  : {item1['label']}"
        )

        print(
            f"Entity 2 : {item2['text']}"
        )

        print(
            f"Label 2  : {item2['label']}"
        )

        print(
            f"\nSimilarity BEFORE : "
            f"{similarity_before:.6f}"
        )

        print(
            f"Similarity AFTER  : "
            f"{similarity_after:.6f}"
        )


if not found:

    print(
        "\nNo same-surface-form/different-label "
        "pairs found."
    )


print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)
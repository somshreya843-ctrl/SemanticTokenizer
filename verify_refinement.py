import torch
import torch.nn.functional as F


# ============================================================
# FILES
# ============================================================

ORIGINAL_FILE = (
    "data/embeddings/test_embeddings.pt"
)

REFINED_FILE = (
    "data/embeddings/refined_embeddings.pt"
)

DATASET_FILE = (
    "data/embeddings/contrastive_dataset.pt"
)


# ============================================================
# LOAD DATA
# ============================================================

print("\n" + "=" * 80)
print("LOADING EMBEDDINGS")
print("=" * 80)

original_data = torch.load(
    ORIGINAL_FILE,
    weights_only=False
)

refined_data = torch.load(
    REFINED_FILE,
    weights_only=False
)

pairs = torch.load(
    DATASET_FILE,
    weights_only=False
)

print(
    f"Original embeddings : {len(original_data)}"
)

print(
    f"Refined embeddings  : {len(refined_data)}"
)

print(
    f"Contrastive pairs   : {len(pairs)}"
)


# ============================================================
# CREATE INDEX MAP
# ============================================================

original_embeddings = {}

refined_embeddings = {}

for index, item in enumerate(original_data):

    original_embeddings[index] = (
        item["embedding"]
    )

    refined_embeddings[index] = (
        refined_data[index]["refined_embedding"]
    )


# ============================================================
# CALCULATE SIMILARITIES
# ============================================================

positive_before = []
positive_after = []

negative_before = []
negative_after = []

hard_negative_before = []
hard_negative_after = []


for pair in pairs:

    idx1 = pair["index1"]
    idx2 = pair["index2"]

    emb1_before = (
        original_embeddings[idx1]
        .unsqueeze(0)
    )

    emb2_before = (
        original_embeddings[idx2]
        .unsqueeze(0)
    )

    emb1_after = (
        refined_embeddings[idx1]
        .unsqueeze(0)
    )

    emb2_after = (
        refined_embeddings[idx2]
        .unsqueeze(0)
    )

    similarity_before = (
        F.cosine_similarity(
            emb1_before,
            emb2_before
        ).item()
    )

    similarity_after = (
        F.cosine_similarity(
            emb1_after,
            emb2_after
        ).item()
    )

    # --------------------------------------------------------
    # Positive
    # --------------------------------------------------------

    if pair["label"] == 1:

        positive_before.append(
            similarity_before
        )

        positive_after.append(
            similarity_after
        )

    # --------------------------------------------------------
    # Negative
    # --------------------------------------------------------

    else:

        negative_before.append(
            similarity_before
        )

        negative_after.append(
            similarity_after
        )

        # ----------------------------------------------------
        # Hard negative
        # ----------------------------------------------------

        if pair.get("pair_type") == "hard_negative":

            hard_negative_before.append(
                similarity_before
            )

            hard_negative_after.append(
                similarity_after
            )


# ============================================================
# HELPER
# ============================================================

def mean(values):

    if not values:
        return None

    return sum(values) / len(values)


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 80)
print("SIMILARITY VALIDATION")
print("=" * 80)


print("\nPOSITIVE PAIRS")

print(
    f"Count             : {len(positive_before)}"
)

print(
    f"Mean similarity BEFORE : "
    f"{mean(positive_before):.6f}"
)

print(
    f"Mean similarity AFTER  : "
    f"{mean(positive_after):.6f}"
)


print("\nNORMAL + HARD NEGATIVE PAIRS")

print(
    f"Count             : {len(negative_before)}"
)

print(
    f"Mean similarity BEFORE : "
    f"{mean(negative_before):.6f}"
)

print(
    f"Mean similarity AFTER  : "
    f"{mean(negative_after):.6f}"
)


# ============================================================
# HARD NEGATIVE
# ============================================================

print("\n" + "=" * 80)
print("HARD NEGATIVE VALIDATION")
print("=" * 80)


if hard_negative_before:

    print(
        "Pair: Jordan (COUNTRY) ↔ Jordan (CITY)"
    )

    print(
        f"Similarity BEFORE : "
        f"{hard_negative_before[0]:.6f}"
    )

    print(
        f"Similarity AFTER  : "
        f"{hard_negative_after[0]:.6f}"
    )

else:

    print(
        "No hard negative pair found."
    )


# ============================================================
# SEPARATION
# ============================================================

positive_mean_before = mean(
    positive_before
)

positive_mean_after = mean(
    positive_after
)

negative_mean_before = mean(
    negative_before
)

negative_mean_after = mean(
    negative_after
)


print("\n" + "=" * 80)
print("POSITIVE / NEGATIVE SEPARATION")
print("=" * 80)


print(
    f"Separation BEFORE : "
    f"{positive_mean_before - negative_mean_before:.6f}"
)

print(
    f"Separation AFTER  : "
    f"{positive_mean_after - negative_mean_after:.6f}"
)
import torch
from pathlib import Path

from src.entities.contrastive_model import (
    ContrastiveRefinementModel
)


# ============================================================
# CONFIGURATION
# ============================================================

EMBEDDINGS_FILE = (
    "data/embeddings/test_embeddings.pt"
)

MODEL_FILE = (
    "data/embeddings/contrastive_model.pt"
)

OUTPUT_FILE = (
    "data/embeddings/refined_embeddings.pt"
)

INPUT_DIM = 768
HIDDEN_DIM = 512
OUTPUT_DIM = 256


# ============================================================
# DEVICE
# ============================================================

device = torch.device(

    "mps"
    if torch.backends.mps.is_available()

    else
    "cuda"
    if torch.cuda.is_available()

    else
    "cpu"
)

print(
    f"Using device: {device}"
)


# ============================================================
# LOAD ORIGINAL EMBEDDINGS
# ============================================================

print("\n" + "=" * 80)
print("LOADING ORIGINAL EMBEDDINGS")
print("=" * 80)

data = torch.load(
    EMBEDDINGS_FILE,
    weights_only=False
)

print(
    f"Total entity embeddings: {len(data)}"
)


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

print("\n" + "=" * 80)
print("LOADING CONTRASTIVE MODEL")
print("=" * 80)

checkpoint = torch.load(
    MODEL_FILE,
    map_location=device,
    weights_only=False
)

model = ContrastiveRefinementModel(

    input_dim=checkpoint["input_dim"],

    hidden_dim=checkpoint["hidden_dim"],

    output_dim=checkpoint["output_dim"]

).to(device)


model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


print(
    "Contrastive refinement model loaded."
)


# ============================================================
# GENERATE REFINED EMBEDDINGS
# ============================================================

print("\n" + "=" * 80)
print("GENERATING REFINED EMBEDDINGS")
print("=" * 80)


refined_data = []


with torch.no_grad():

    for i, item in enumerate(data):

        original_embedding = (
            item["embedding"]
            .float()
            .unsqueeze(0)
            .to(device)
        )

        # ----------------------------------------------
        # Pass through trained refinement model
        # ----------------------------------------------

        refined_embedding = model(
            original_embedding
        )

        # ----------------------------------------------
        # Move back to CPU
        # ----------------------------------------------

        refined_embedding = (
            refined_embedding
            .squeeze(0)
            .cpu()
        )

        # ----------------------------------------------
        # Copy metadata
        # ----------------------------------------------

        refined_item = {

            "text":
                item["text"],

            "label":
                item["label"],

            "start":
                item["start"],

            "end":
                item["end"],

            "source":
                item.get("source"),

            "placeholder":
                item.get("placeholder"),

            "original_embedding":
                item["embedding"],

            "refined_embedding":
                refined_embedding
        }

        refined_data.append(
            refined_item
        )

        print(
            f"{i + 1:03d}/{len(data)} "
            f"| {item['text']} "
            f"| {item['label']} "
            f"| "
            f"{refined_embedding.shape}"
        )


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

Path(
    "data/embeddings"
).mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SAVE REFINED EMBEDDINGS
# ============================================================

torch.save(
    refined_data,
    OUTPUT_FILE
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("REFINEMENT COMPLETE")
print("=" * 80)

print(
    f"Original embedding dimension : "
    f"{INPUT_DIM}"
)

print(
    f"Refined embedding dimension  : "
    f"{OUTPUT_DIM}"
)

print(
    f"Total refined embeddings     : "
    f"{len(refined_data)}"
)

print(
    f"Saved to                      : "
    f"{OUTPUT_FILE}"
)
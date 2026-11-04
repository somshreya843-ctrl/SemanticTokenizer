import torch
from torch.utils.data import Dataset, DataLoader

from src.entities.contrastive_model import (
    ContrastiveRefinementModel
)

from src.entities.contrastive_loss import (
    ContrastiveLoss
)


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_FILE = (
    "data/embeddings/contrastive_dataset.pt"
)

MODEL_FILE = (
    "data/embeddings/contrastive_model.pt"
)

BATCH_SIZE = 32
EPOCHS = 20
LEARNING_RATE = 1e-3

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
# LOAD DATASET
# ============================================================

pairs = torch.load(
    DATASET_FILE,
    weights_only=False
)

print(
    f"Loaded pairs: {len(pairs)}"
)


# ============================================================
# DATASET CLASS
# ============================================================

class ContrastivePairDataset(Dataset):

    def __init__(self, pairs):

        self.pairs = pairs

    def __len__(self):

        return len(self.pairs)

    def __getitem__(self, index):

        pair = self.pairs[index]

        embedding1 = pair[
            "embedding1"
        ].float()

        embedding2 = pair[
            "embedding2"
        ].float()

        label = torch.tensor(
            pair["label"],
            dtype=torch.float32
        )

        return (
            embedding1,
            embedding2,
            label
        )


# ============================================================
# CREATE DATALOADER
# ============================================================

dataset = ContrastivePairDataset(
    pairs
)

dataloader = DataLoader(
    dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)


# ============================================================
# MODEL
# ============================================================

model = ContrastiveRefinementModel(

    input_dim=INPUT_DIM,

    hidden_dim=HIDDEN_DIM,

    output_dim=OUTPUT_DIM

).to(device)


# ============================================================
# LOSS
# ============================================================

criterion = ContrastiveLoss(
    margin=0.5
)


# ============================================================
# OPTIMIZER
# ============================================================

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)


# ============================================================
# TRAINING
# ============================================================

print("\n" + "=" * 80)
print("CONTRASTIVE REFINEMENT TRAINING")
print("=" * 80)

for epoch in range(
    EPOCHS
):

    model.train()

    total_loss = 0.0

    for (
        embedding1,
        embedding2,
        labels
    ) in dataloader:

        embedding1 = embedding1.to(
            device
        )

        embedding2 = embedding2.to(
            device
        )

        labels = labels.to(
            device
        )

        # --------------------------------------------------
        # Forward pass
        # --------------------------------------------------

        refined1 = model(
            embedding1
        )

        refined2 = model(
            embedding2
        )

        # --------------------------------------------------
        # Contrastive loss
        # --------------------------------------------------

        loss = criterion(
            refined1,
            refined2,
            labels
        )

        # --------------------------------------------------
        # Backpropagation
        # --------------------------------------------------

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

        total_loss += (
            loss.item()
        )

    average_loss = (
        total_loss /
        len(dataloader)
    )

    print(
        f"Epoch "
        f"{epoch + 1:02d}/{EPOCHS} "
        f"| Loss: "
        f"{average_loss:.6f}"
    )


# ============================================================
# SAVE MODEL
# ============================================================

torch.save(
    {
        "model_state_dict":
            model.state_dict(),

        "input_dim":
            INPUT_DIM,

        "hidden_dim":
            HIDDEN_DIM,

        "output_dim":
            OUTPUT_DIM
    },
    MODEL_FILE
)


print("\n" + "=" * 80)
print("TRAINING COMPLETE")
print("=" * 80)

print(
    f"Model saved to: {MODEL_FILE}"
)
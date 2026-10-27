import torch
import torch.nn as nn
import torch.nn.functional as F


class ContrastiveLoss(nn.Module):

    def __init__(self, margin=0.5):

        super().__init__()

        self.margin = margin

    def forward(
        self,
        embedding1,
        embedding2,
        labels
    ):

        # --------------------------------------------------
        # Cosine similarity
        # --------------------------------------------------

        similarity = F.cosine_similarity(
            embedding1,
            embedding2
        )

        # --------------------------------------------------
        # Positive pairs:
        # We want similarity → 1
        # --------------------------------------------------

        positive_loss = (
            labels *
            (1 - similarity).pow(2)
        )

        # --------------------------------------------------
        # Negative pairs:
        # We want similarity < margin
        # --------------------------------------------------

        negative_loss = (
            (1 - labels) *
            torch.clamp(
                similarity - self.margin,
                min=0
            ).pow(2)
        )

        loss = (
            positive_loss +
            negative_loss
        )

        return loss.mean()
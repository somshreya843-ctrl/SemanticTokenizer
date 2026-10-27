import torch
import torch.nn as nn
import torch.nn.functional as F


class ContrastiveRefinementModel(nn.Module):

    def __init__(
        self,
        input_dim=768,
        hidden_dim=512,
        output_dim=256
    ):

        super().__init__()

        self.network = nn.Sequential(

            nn.Linear(
                input_dim,
                hidden_dim
            ),

            nn.ReLU(),

            nn.Linear(
                hidden_dim,
                output_dim
            )
        )

    def forward(self, x):

        embedding = self.network(x)

        # Normalize embeddings so that cosine similarity
        # can be used effectively.
        embedding = F.normalize(
            embedding,
            p=2,
            dim=1
        )

        return embedding
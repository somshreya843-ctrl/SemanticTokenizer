from pathlib import Path
import torch


class BatchedContextEmbedder:

    def __init__(
        self,
        context_embedder,
        batch_size=32,
        shard_size=10000,
        output_dir="data/embeddings/grounded_shards"
    ):
        self.context_embedder = context_embedder
        self.batch_size = batch_size
        self.shard_size = shard_size

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # =========================================================
    # Encode one batch
    # =========================================================

    def _encode_batch(self, batch):

        embeddings = []

        for item in batch:

            embedding = self.context_embedder.encode(
                context=item["sentence"],
                entity=item["entity"],
                category=item["type"]
            )

            embeddings.append(
                embedding
            )

        return embeddings

    # =========================================================
    # Process grounded records
    # =========================================================

    def process(self, records):

        batch = []
        shard = []
        shard_id = 0
        total = 0

        for record in records:

            batch.append(record)

            if len(batch) >= self.batch_size:

                embeddings = self._encode_batch(
                    batch
                )

                for record, embedding in zip(
                    batch,
                    embeddings
                ):

                    item = dict(record)

                    item["embedding"] = embedding

                    shard.append(item)

                    total += 1

                batch = []

                if len(shard) >= self.shard_size:

                    self._save_shard(
                        shard,
                        shard_id
                    )

                    shard = []

                    shard_id += 1

        # -----------------------------------------------------
        # Remaining records
        # -----------------------------------------------------

        if batch:

            embeddings = self._encode_batch(
                batch
            )

            for record, embedding in zip(
                batch,
                embeddings
            ):

                item = dict(record)

                item["embedding"] = embedding

                shard.append(item)

                total += 1

        # -----------------------------------------------------
        # Save final shard
        # -----------------------------------------------------

        if shard:

            self._save_shard(
                shard,
                shard_id
            )

        print("=" * 60)
        print("GROUNDED SENTENCE EMBEDDING COMPLETE")
        print("=" * 60)
        print(f"Total embeddings : {total}")
        print(f"Total shards     : {shard_id + 1}")

    # =========================================================
    # Save shard
    # =========================================================

    def _save_shard(
        self,
        shard,
        shard_id
    ):

        output_file = (
            self.output_dir /
            f"embeddings_{shard_id:05d}.pt"
        )

        torch.save(
            shard,
            output_file
        )

        print(
            f"Saved shard {shard_id}: "
            f"{len(shard)} embeddings → "
            f"{output_file}"
        )
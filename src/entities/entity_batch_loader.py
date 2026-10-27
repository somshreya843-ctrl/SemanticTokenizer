from pathlib import Path


class EntityBatchLoader:

    def __init__(
        self,
        entity_dir="data/entities",
        batch_size=1024
    ):
        self.entity_dir = Path(entity_dir)
        self.batch_size = batch_size

    def iter_entities(self):

        for file_path in sorted(
            self.entity_dir.rglob("*.txt")
        ):

            category = file_path.parent.name
            label = file_path.stem

            print(f"Reading: {file_path}")

            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                for line_number, line in enumerate(f, start=1):

                    entity = line.strip()

                    if not entity:
                        continue

                    yield {
                        "text": entity,
                        "label": label,
                        "category": category,
                        "source_file": file_path.name,
                        "line_number": line_number
                    }

    def iter_batches(self):

        batch = []

        for entity in self.iter_entities():

            batch.append(entity)

            if len(batch) >= self.batch_size:

                yield batch
                batch = []

        if batch:
            yield batch
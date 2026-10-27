from pathlib import Path

from providers.registry import ProviderRegistry
from .writer import EntityWriter
from .pipeline import EntityPipeline


class EntityBuilder:

    def __init__(self, source):

        self.source = source
        self.provider = ProviderRegistry.get_provider(source.provider)

    def build(self):

        output = (
            Path("data")
            / "entities"
            / self.source.category
            / f"{self.source.name}.txt"
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        writer = EntityWriter(
            output,
            self.source.encoding,
        )

        seen = set()

        raw_records = 0
        filtered_records = 0
        duplicate_records = 0
        written_records = 0

        try:

            for record in self.provider.fetch(self.source):

                raw_records += 1

                try:

                    value = record.get(self.source.column)

                    if not isinstance(value, str):
                        filtered_records += 1
                        continue

                    value = value.strip()

                    if not value:
                        filtered_records += 1
                        continue

                    ####################################################
                    # Normalize + Alias Generation + Quality Filtering
                    ####################################################

                    aliases = EntityPipeline.process(
                        value,
                        self.source.name
                    )

                    if not aliases:
                        filtered_records += 1
                        continue

                    ####################################################
                    # Deduplicate
                    ####################################################

                    for entity in aliases:

                        key = entity.casefold()

                        if key in seen:
                            duplicate_records += 1
                            continue

                        seen.add(key)

                        writer.write(entity)

                        written_records += 1

                except Exception as e:

                    print(
                        f"[WARNING] Skipping malformed record in "
                        f"{self.source.name}: {e}"
                    )

                    filtered_records += 1

        finally:

            writer.close()

        print()
        print("=" * 70)
        print(f"{self.source.category}/{self.source.name}")
        print("=" * 70)
        print(f"Raw records      : {raw_records}")
        print(f"Filtered         : {filtered_records}")
        print(f"Duplicates       : {duplicate_records}")
        print(f"Written          : {written_records}")
        print(f"Output           : {output}")
        print("=" * 70)
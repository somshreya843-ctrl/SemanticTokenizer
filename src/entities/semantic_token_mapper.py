
import json
from pathlib import Path


class SemanticTokenMapper:
    def __init__(
        self,
        registry_file="data/entities/semantic_id_registry.json",
        mapping_file="data/entities/semantic_token_mapping.json",
    ):
        self.registry_file = Path(registry_file)
        self.mapping_file = Path(mapping_file)
        self.mapping_file.parent.mkdir(parents=True, exist_ok=True)

    def run(self):
        with open(self.registry_file, "r", encoding="utf-8") as f:
            registry = json.load(f)

        if self.mapping_file.exists():
            with open(self.mapping_file, "r", encoding="utf-8") as f:
                mapping = json.load(f)
        else:
            mapping = {"version": 1, "tokens": {}}

        tokens = mapping.setdefault("tokens", {})

        for record in registry["records"].values():
            semantic_id = record["semantic_id"]
            candidate_types = sorted({
                str(t).strip().upper()
                for t in record.get("candidate_types", [])
                if str(t).strip()
            })

            # Assign a specific type only when exactly one candidate exists.
            # Keep ambiguous entities generic until their sense is resolved.
            known_types = {
                "PERSON", "COMPANY", "ORGANIZATION", "COUNTRY", "CITY",
                "STATE", "LOCATION", "LANGUAGE", "PROGRAMMING_LANGUAGE",
                "FOOD", "ANIMAL", "PLANT", "SOFTWARE", "MOVIE", "BOOK",
                "ACTOR", "MUSICIAN", "AUTHOR", "MEDICINE", "METAL",
                "CHEMICAL_ELEMENT", "GAS", "MEDIA_FORMAT", "CURRENCY",
                "DATE", "EMAIL", "PHONE", "URL", "IP", "PINCODE"
            }

            if (
                not candidate_types
                or "UNKNOWN" in candidate_types
                or "ENTITY" in candidate_types
            ):
                category = "UNKNOWN"
            elif len(candidate_types) == 1 and candidate_types[0] in known_types:
                category = candidate_types[0]
            else:
                # Multiple unresolved candidate types: do not guess.
                category = "UNKNOWN"

            # Rebuild the entry so existing mappings are corrected too.
            tokens[semantic_id] = {
                "placeholder": f"<{category}_{semantic_id}>",
                "entity": record["entity"],
                "candidate_types": candidate_types,
            }

        with open(self.mapping_file, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)

        print("Semantic token mapping created/updated.")
        print(f"Total semantic tokens: {len(tokens)}")
        print(f"Output: {self.mapping_file}")


if __name__ == "__main__":
    SemanticTokenMapper().run()

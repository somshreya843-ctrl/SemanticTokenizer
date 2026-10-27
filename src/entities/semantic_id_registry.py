
import json
import hashlib
from pathlib import Path


class SemanticIDRegistry:
    def __init__(
        self,
        tree_file="data/clusters/semantic_entity_tree.json",
        registry_file="data/entities/semantic_id_registry.json",
    ):
        self.tree_file = Path(tree_file)
        self.registry_file = Path(registry_file)
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)

    def load_tree(self):
        with open(self.tree_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def collect_senses(self, node, senses):
        for member in node.get("members", []):
            entity = member["entity"].casefold().strip()
            sense_id = member["sense_id"]

            # Include contexts and types to distinguish senses.
            identity_data = {
                "entity": entity,
                "sense_id": sense_id,
                "candidate_types": sorted(member.get("candidate_types", [])),
                "contexts": sorted(
                    context.get("sentence", "").strip()
                    for context in member.get("contexts", [])
                ),
            }

            identity_key = json.dumps(
                identity_data,
                sort_keys=True,
                ensure_ascii=False,
            )

            identity_hash = hashlib.sha256(
                identity_key.encode("utf-8")
            ).hexdigest()

            senses[identity_hash] = identity_data

        for child in node.get("children", []):
            self.collect_senses(child, senses)

    def run(self):
        tree = self.load_tree()

        senses = {}
        self.collect_senses(tree["tree"], senses)

        if self.registry_file.exists():
            with open(self.registry_file, "r", encoding="utf-8") as f:
                registry = json.load(f)
        else:
            registry = {"version": 1, "records": {}}

        records = registry["records"]

        # Preserve existing IDs; assign IDs only to new identities.
        used_ids = {
            record["semantic_id"]
            for record in records.values()
        }

        next_number = 1
        for identity_hash, identity_data in sorted(senses.items()):
            if identity_hash in records:
                continue

            while f"SEM_{next_number:06d}" in used_ids:
                next_number += 1

            semantic_id = f"SEM_{next_number:06d}"

            records[identity_hash] = {
                **identity_data,
                "semantic_id": semantic_id,
            }

            used_ids.add(semantic_id)
            next_number += 1

        registry["records"] = records

        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

        print("Semantic ID registry created/updated.")
        print(f"Unique senses in current tree: {len(senses)}")
        print(f"Total registered senses: {len(records)}")
        print(f"Registry: {self.registry_file}")


if __name__ == "__main__":
    SemanticIDRegistry().run()

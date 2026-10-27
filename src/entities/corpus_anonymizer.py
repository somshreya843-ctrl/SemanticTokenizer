
import json
import re
from pathlib import Path


class CorpusAnonymizer:
    def __init__(
        self,
        token_mapping_file="data/entities/semantic_token_mapping.json",
        registry_file="data/entities/semantic_id_registry.json",
        output_file="data/corpus/semantic_corpus.txt",
        audit_file="data/corpus/anonymization_audit.jsonl",
    ):
        self.token_mapping_file = Path(token_mapping_file)
        self.registry_file = Path(registry_file)
        self.output_file = Path(output_file)
        self.audit_file = Path(audit_file)

        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def load_data(self):
        with open(self.token_mapping_file, encoding="utf-8") as f:
            mapping = json.load(f)["tokens"]

        with open(self.registry_file, encoding="utf-8") as f:
            registry = json.load(f)["records"]

        return mapping, registry

    def build_patterns(self, mapping, registry):
        patterns = []

        for identity_hash, record in registry.items():
            entity = record["entity"]
            semantic_id = record["semantic_id"]

            token_record = mapping.get(semantic_id)
            if not token_record:
                continue

            # Preserve all candidate types.
            # The semantic token mapper assigns generic ENTITY placeholders
            # to ambiguous entities instead of choosing an arbitrary type.
            types = record.get("candidate_types", [])

            pattern = re.compile(
                r"(?<!\w)" + re.escape(entity) + r"(?!\w)",
                re.IGNORECASE,
            )

            patterns.append({
                "pattern": pattern,
                "entity": entity,
                "semantic_id": semantic_id,
                "placeholder": token_record["placeholder"],
                "candidate_types": types,
            })

        # Prefer longer names, such as "New York", before shorter names.
        patterns.sort(key=lambda item: len(item["entity"]), reverse=True)

        return patterns

    def anonymize_text(self, text, patterns, audit_file):
        for item in patterns:
            def replace(match):
                audit_file.write(json.dumps({
                    "original": match.group(0),
                    "placeholder": item["placeholder"],
                    "semantic_id": item["semantic_id"],
                    "candidate_types": item["candidate_types"],
                    "start": match.start(),
                    "end": match.end(),
                }, ensure_ascii=False) + "\n")

                return item["placeholder"]

            text = item["pattern"].sub(replace, text)

        return text

    def run(self, input_file):
        mapping, registry = self.load_data()
        patterns = self.build_patterns(mapping, registry)

        input_file = Path(input_file)

        with open(input_file, encoding="utf-8") as src, \
             open(self.output_file, "w", encoding="utf-8") as dst, \
             open(self.audit_file, "w", encoding="utf-8") as audit:

            for line in src:
                dst.write(self.anonymize_text(line, patterns, audit))

        print("Corpus anonymization complete.")
        print(f"Input: {input_file}")
        print(f"Output: {self.output_file}")
        print(f"Audit: {self.audit_file}")
        print(f"Patterns: {len(patterns)}")


if __name__ == "__main__":
    anonymizer = CorpusAnonymizer()

    # Replace this path with a plain-text WikiText-2 file
    # that you have already downloaded or exported.
    anonymizer.run("data/corpus/wikitext2_sample.txt")

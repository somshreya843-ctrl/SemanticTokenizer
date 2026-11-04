from datasets import load_dataset
from src.corpus_processor import CorpusProcessor
import json
import os

OUTPUT_FILE = "data/grounded/wikitext2_grounding_test.jsonl"

dataset = load_dataset(
    "Salesforce/wikitext",
    "wikitext-2-raw-v1"
)

processor = CorpusProcessor(
    grounded_output="data/grounded/wikitext2_grounding_test.jsonl"
)

# Collect only the records generated during this WikiText-2 run
all_records = []

count = 0

for sample in dataset["train"]:

    text = sample["text"].strip()

    if len(text) < 100:
        continue

    print("=" * 60)
    print(f"WikiText-2 Document {count + 1}")

    # Stage-A grounding is written by CorpusProcessor
    processor.process_document(text)

    count += 1

    if count == 10:
        break


# Read and report records from the dedicated grounding test file.
source_file = "data/grounded/wikitext2_grounding_test.jsonl"

all_records = []

if os.path.exists(source_file):
    with open(source_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                all_records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

print("=" * 60)
print("WIKITEXT-2 GROUNDING COMPLETE")
print("=" * 60)
print("Documents processed:", count)
print("Records in test output:", len(all_records))
print("Output:", source_file)

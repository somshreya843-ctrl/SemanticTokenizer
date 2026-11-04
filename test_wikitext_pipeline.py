from datasets import load_dataset
from src.corpus_processor import CorpusProcessor

# Load WikiText
dataset = load_dataset(
    "Salesforce/wikitext",
    "wikitext-2-raw-v1"
)

processor = CorpusProcessor()

count = 0

for sample in dataset["train"]:

    text = sample["text"].strip()

    # Skip empty or very short lines
    if len(text) < 100:
        continue

    print("=" * 80)
    print(f"Document {count + 1}")

    semantic_text, entities = processor.process_document(text)

    print("\nORIGINAL:\n")
    print(text[:500])

    print("\nSEMANTIC:\n")
    print(semantic_text[:500])

    print("\nENTITIES:")

    for entity in entities:
        print(entity)

    count += 1

    if count == 10:
        break
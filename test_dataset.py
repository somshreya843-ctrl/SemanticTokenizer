from datasets import load_dataset

dataset = load_dataset(
    "Salesforce/wikitext",
    "wikitext-2-raw-v1"
)

count = 0

for sample in dataset["train"]:

    text = sample["text"].strip()

    # Skip blank lines
    if text == "":
        continue

    # Skip very short lines (titles only)
    if len(text) < 100:
        continue

    print("=" * 80)
    print(text)
    print()

    count += 1

    if count == 5:
        break
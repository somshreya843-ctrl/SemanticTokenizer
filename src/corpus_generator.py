import json
from pathlib import Path

from datasets import load_dataset

from src.corpus_processor import CorpusProcessor


class CorpusGenerator:

    def __init__(self):

        self.processor = CorpusProcessor()

    def generate(
        self,
        max_documents=100,
        output_folder="output"
    ):

        dataset = load_dataset(
            "Salesforce/wikitext",
            "wikitext-2-raw-v1"
        )

        output_folder = Path(output_folder)

        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        semantic_file = output_folder / "semantic_corpus.txt"
        parsed_file = output_folder / "parsed_corpus.txt"

        map_folder = output_folder / "entity_maps"

        map_folder.mkdir(
            exist_ok=True
        )

        processed = 0

        with open(
            semantic_file,
            "w",
            encoding="utf-8"
        ) as corpus, open(
            parsed_file,
            "w",
            encoding="utf-8"
        ) as parsed_corpus:

            for sample in dataset["train"]:

                text = sample["text"].strip()

                if len(text) < 100:
                    continue

                semantic_text, entities = self.processor.process_document(
                    text
                )

                #########################################################
                # Generate Parsed Corpus
                #########################################################

                parsed_segments = self.processor.lookup.parse(
                    text,
                    doc_id=f"DOC{processed+1:04d}"
                )

                for item in parsed_segments:

                    parsed_corpus.write(
                        f"{item['id']}|"
                        f"{item['original']}|"
                        f"{item['parsed']}|"
                        f"{item['metadata']}\n"
                    )

                corpus.write(semantic_text)
                corpus.write("\n\n")

                entity_dict = {}

                for entity in entities:

                    entity_dict[
                        entity["placeholder"]
                    ] = entity["text"]

                json_file = (
                    map_folder
                    / f"doc_{processed+1:06d}.json"
                )

                with open(
                    json_file,
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        entity_dict,
                        f,
                        indent=4,
                        ensure_ascii=False
                    )

                processed += 1

                print(
                    f"Processed {processed}"
                )

                if processed >= max_documents:
                    break

        print("\nCorpus Generation Finished")
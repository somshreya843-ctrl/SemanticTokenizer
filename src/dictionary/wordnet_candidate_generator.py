from pathlib import Path
from collections import defaultdict

from nltk.corpus import wordnet as wn


class WordNetCandidateGenerator:
    """
    Generate candidate entity words from WordNet.

    IMPORTANT:
    - Analysis/candidate generation only.
    - Existing entity lists are NOT modified.
    - Candidates are written to a separate directory.
    - No new entity type is automatically accepted.
    """

    # --------------------------------------------------------
    # WordNet category -> proposed SemanticTokenizer category
    # --------------------------------------------------------

    CATEGORY_MAPPING = {
        "noun.person": "PERSON",
        "noun.animal": "ANIMAL",
        "noun.plant": "PLANT",
        "noun.location": "LOCATION",
        "noun.attribute": "ATTRIBUTE",
        "noun.cognition": "CONCEPT",
        "noun.group": "GROUP",
        "noun.food": "FOOD",
        "noun.body": "BODY_PART",
        "noun.object": "OBJECT",
        "noun.quantity": "QUANTITY",
        "noun.event": "EVENT",
        "noun.possession": "POSSESSION",
        "noun.time": "TIME",
        "noun.phenomenon": "PHENOMENON",
        "noun.relation": "RELATION",
        "noun.feeling": "FEELING",
        "noun.shape": "SHAPE",
        "noun.motive": "MOTIVE",
    }

    # --------------------------------------------------------
    # Existing entity directory
    # --------------------------------------------------------

    EXISTING_ENTITY_PATH = Path("data/entities")

    # --------------------------------------------------------
    # Candidate output directory
    # --------------------------------------------------------

    OUTPUT_PATH = Path("data/dictionary_candidates")

    # --------------------------------------------------------
    # Constructor
    # --------------------------------------------------------

    def __init__(self):

        self.existing_entities = self.load_existing_entities()

        print(
            "Loaded existing entity vocabulary:",
            len(self.existing_entities)
        )

    # --------------------------------------------------------
    # Normalize words
    # --------------------------------------------------------

    @staticmethod
    def normalize(word):
        """
        Normalize a WordNet lemma for comparison.
        """

        word = word.replace("_", " ")

        word = " ".join(word.split())

        return word.strip()

    # --------------------------------------------------------
    # Load existing project entity vocabulary
    # --------------------------------------------------------

    def load_existing_entities(self):

        entities = set()

        if not self.EXISTING_ENTITY_PATH.exists():

            print(
                "WARNING: Existing entity directory not found:"
            )

            print(
                self.EXISTING_ENTITY_PATH
            )

            return entities

        for filepath in self.EXISTING_ENTITY_PATH.rglob("*.txt"):

            try:

                with open(
                    filepath,
                    "r",
                    encoding="utf-8"
                ) as f:

                    for line in f:

                        value = line.strip()

                        if not value:
                            continue

                        value = self.normalize(value)

                        if value:
                            entities.add(
                                value.casefold()
                            )

            except Exception as exc:

                print(
                    "Could not read:",
                    filepath,
                    "->",
                    exc
                )

        return entities

    # --------------------------------------------------------
    # Candidate validation
    # --------------------------------------------------------

    @staticmethod
    def is_valid_candidate(word):

        if not word:
            return False

        # Very short words create too many false positives.
        if len(word) < 2:
            return False

        # Ignore purely numeric entries.
        if word.isdigit():
            return False

        # Ignore entries consisting only of punctuation.
        if not any(char.isalpha() for char in word):

            return False

        return True

    # --------------------------------------------------------
    # Get WordNet words for a category
    # --------------------------------------------------------

    def get_words_for_category(self, category):

        words = set()

        for synset in wn.all_synsets(pos="n"):

            if synset.lexname() != category:
                continue

            for lemma in synset.lemmas():

                word = self.normalize(
                    lemma.name()
                )

                if not self.is_valid_candidate(word):
                    continue

                words.add(word)

        return words

    # --------------------------------------------------------
    # Remove words already covered by project
    # --------------------------------------------------------

    def remove_existing_entities(self, words):

        candidates = set()

        for word in words:

            if word.casefold() in self.existing_entities:

                continue

            candidates.add(word)

        return candidates

    # --------------------------------------------------------
    # Generate candidates
    # --------------------------------------------------------

    def generate(self):

        results = {}

        print("\n")
        print("=" * 80)
        print("GENERATING WORDNET CANDIDATES")
        print("=" * 80)

        for wordnet_category, entity_type in self.CATEGORY_MAPPING.items():

            print(
                "\nProcessing:",
                wordnet_category,
                "->",
                entity_type
            )

            words = self.get_words_for_category(
                wordnet_category
            )

            before = len(words)

            candidates = self.remove_existing_entities(
                words
            )

            after = len(candidates)

            results[entity_type] = {
                "wordnet_category": wordnet_category,
                "total_words": before,
                "new_candidates": after,
                "words": candidates,
            }

            print(
                "WordNet words      :",
                before
            )

            print(
                "Already in project :",
                before - after
            )

            print(
                "New candidates     :",
                after
            )

        return results

    # --------------------------------------------------------
    # Write candidate files
    # --------------------------------------------------------

    def write_candidates(self, results):

        self.OUTPUT_PATH.mkdir(
            parents=True,
            exist_ok=True
        )

        print("\n")
        print("=" * 80)
        print("WRITING CANDIDATE FILES")
        print("=" * 80)

        for entity_type, data in results.items():

            filename = (
                entity_type.lower()
                + "_candidates.txt"
            )

            filepath = (
                self.OUTPUT_PATH
                / filename
            )

            words = sorted(
                data["words"],
                key=str.casefold
            )

            with open(
                filepath,
                "w",
                encoding="utf-8"
            ) as f:

                for word in words:

                    f.write(
                        word + "\n"
                    )

            print(
                f"{entity_type:20}"
                f"-> {len(words):6} candidates"
                f" -> {filepath}"
            )

    # --------------------------------------------------------
    # Write summary
    # --------------------------------------------------------

    def write_summary(self, results):

        filepath = (
            self.OUTPUT_PATH
            / "candidate_summary.txt"
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                "WordNet Candidate Generation Summary\n"
            )

            f.write(
                "=" * 80 + "\n\n"
            )

            f.write(
                "IMPORTANT:\n"
            )

            f.write(
                "These are candidate words only.\n"
            )

            f.write(
                "They have NOT been accepted as entity lists.\n"
            )

            f.write(
                "Existing entity lists were not modified.\n\n"
            )

            for entity_type, data in results.items():

                f.write(
                    f"{entity_type}\n"
                )

                f.write(
                    f"  WordNet category : "
                    f"{data['wordnet_category']}\n"
                )

                f.write(
                    f"  Total WordNet words : "
                    f"{data['total_words']}\n"
                )

                f.write(
                    f"  New candidates : "
                    f"{data['new_candidates']}\n"
                )

                f.write("\n")

        print(
            "\nSummary written to:",
            filepath
        )

    # --------------------------------------------------------
    # Print examples
    # --------------------------------------------------------

    def print_examples(
        self,
        results,
        limit=20
    ):

        print("\n")
        print("=" * 80)
        print("CANDIDATE EXAMPLES")
        print("=" * 80)

        for entity_type, data in results.items():

            words = sorted(
                data["words"],
                key=str.casefold
            )

            print("\n" + "-" * 80)

            print(
                entity_type,
                "<-",
                data["wordnet_category"]
            )

            print("-" * 80)

            for word in words[:limit]:

                print(
                    " ",
                    word
                )

    # --------------------------------------------------------
    # Run complete process
    # --------------------------------------------------------

    def run(self):

        print("=" * 80)
        print("WordNet -> Candidate Entity Generator")
        print("=" * 80)

        print(
            "\nExisting entity lists are NOT modified."
        )

        print(
            "Candidates will be written to:"
        )

        print(
            self.OUTPUT_PATH
        )

        results = self.generate()

        self.write_candidates(
            results
        )

        self.write_summary(
            results
        )

        self.print_examples(
            results,
            limit=20
        )

        print("\n")
        print("=" * 80)
        print("CANDIDATE GENERATION COMPLETE")
        print("=" * 80)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    generator = WordNetCandidateGenerator()

    generator.run()
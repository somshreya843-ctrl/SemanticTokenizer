from pathlib import Path
from collections import defaultdict

from nltk.corpus import wordnet as wn


class WordNetCandidateFilter:
    """
    Conservative quality filter for WordNet-generated candidates.

    IMPORTANT:
    - Does NOT modify existing entity lists.
    - Does NOT automatically add candidates to the project.
    - Keeps the original candidate files unchanged.
    - Writes filtered candidates separately.
    """

    INPUT_PATH = Path("data/dictionary_candidates")
    OUTPUT_PATH = Path("data/dictionary_candidates/filtered")

    # --------------------------------------------------------
    # Categories where broad/general nouns are not useful
    # as entity-list entries without additional evidence.
    # --------------------------------------------------------

    CATEGORY_RULES = {

        "animal": {
            "wordnet_category": "noun.animal",
            "remove_generic": True,
        },

        "plant": {
            "wordnet_category": "noun.plant",
            "remove_generic": True,
        },

        "person": {
            "wordnet_category": "noun.person",
            "remove_generic": True,
        },

        "location": {
            "wordnet_category": "noun.location",
            "remove_generic": True,
        },

        "food": {
            "wordnet_category": "noun.food",
            "remove_generic": True,
        },

        "body_part": {
            "wordnet_category": "noun.body",
            "remove_generic": True,
        },

        "group": {
            "wordnet_category": "noun.group",
            "remove_generic": True,
        },

        "attribute": {
            "wordnet_category": "noun.attribute",
            "remove_generic": True,
        },

        "concept": {
            "wordnet_category": "noun.cognition",
            "remove_generic": True,
        },

        "object": {
            "wordnet_category": "noun.object",
            "remove_generic": True,
        },

        "quantity": {
            "wordnet_category": "noun.quantity",
            "remove_generic": True,
        },

        "event": {
            "wordnet_category": "noun.event",
            "remove_generic": True,
        },

        "possession": {
            "wordnet_category": "noun.possession",
            "remove_generic": True,
        },

        "time": {
            "wordnet_category": "noun.time",
            "remove_generic": True,
        },

        "phenomenon": {
            "wordnet_category": "noun.phenomenon",
            "remove_generic": True,
        },

        "relation": {
            "wordnet_category": "noun.relation",
            "remove_generic": True,
        },

        "feeling": {
            "wordnet_category": "noun.feeling",
            "remove_generic": True,
        },

        "shape": {
            "wordnet_category": "noun.shape",
            "remove_generic": True,
        },

        "motive": {
            "wordnet_category": "noun.motive",
            "remove_generic": True,
        },
    }

    # --------------------------------------------------------
    # Very broad words that should not become entity entries.
    #
    # This list is deliberately small.
    # We do NOT aggressively remove unusual scientific names.
    # --------------------------------------------------------

    GENERIC_WORDS = {
        "entity",
        "thing",
        "object",
        "something",
        "anything",
        "everything",
        "nothing",
        "person",
        "people",
        "individual",
        "someone",
        "somebody",
        "animal",
        "plant",
        "food",
        "location",
        "place",
        "area",
        "region",
        "group",
        "attribute",
        "property",
        "concept",
        "idea",
        "event",
        "object",
        "body",
        "part",
        "shape",
        "quantity",
        "relation",
        "feeling",
        "motive",
        "time",
        "process",
        "state",
    }

    # --------------------------------------------------------
    # Words that are usually too short/generic for discovery.
    # --------------------------------------------------------

    SHORT_GENERIC_WORDS = {
        "a",
        "an",
        "am",
        "as",
        "at",
        "be",
        "by",
        "do",
        "go",
        "he",
        "if",
        "in",
        "is",
        "it",
        "me",
        "my",
        "no",
        "of",
        "on",
        "or",
        "so",
        "to",
        "up",
        "us",
        "we",
    }

    # --------------------------------------------------------
    # Constructor
    # --------------------------------------------------------

    def __init__(self):

        self.stats = defaultdict(
            lambda: {
                "input": 0,
                "kept": 0,
                "removed_generic": 0,
                "removed_short": 0,
                "removed_non_alpha": 0,
            }
        )

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    @staticmethod
    def normalize(word):

        word = " ".join(
            word.replace("_", " ").split()
        )

        return word.strip()

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    def basic_valid(self, word):

        if not word:
            return False

        if len(word) < 2:
            return False

        # Ignore entries with no alphabetic character.
        if not any(
            character.isalpha()
            for character in word
        ):
            return False

        return True

    # --------------------------------------------------------
    # Generic-word check
    # --------------------------------------------------------

    def is_generic(self, word):

        normalized = word.casefold()

        if normalized in self.GENERIC_WORDS:
            return True

        return False

    # --------------------------------------------------------
    # Short-word check
    # --------------------------------------------------------

    def is_short_generic(self, word):

        return (
            word.casefold()
            in self.SHORT_GENERIC_WORDS
        )

    # --------------------------------------------------------
    # Candidate filtering
    # --------------------------------------------------------

    def filter_candidate(
        self,
        word,
        category
    ):
        """
        Return:

            True  -> keep
            False -> remove
        """

        stats = self.stats[category]

        stats["input"] += 1

        word = self.normalize(word)

        # --------------------------------------------
        # Basic validation
        # --------------------------------------------

        if not self.basic_valid(word):

            stats["removed_non_alpha"] += 1

            return False

        # --------------------------------------------
        # Very short generic words
        # --------------------------------------------

        if self.is_short_generic(word):

            stats["removed_short"] += 1

            return False

        # --------------------------------------------
        # Broad semantic words
        # --------------------------------------------

        if self.is_generic(word):

            stats["removed_generic"] += 1

            return False

        # --------------------------------------------
        # Keep candidate
        # --------------------------------------------

        stats["kept"] += 1

        return True

    # --------------------------------------------------------
    # Read candidate file
    # --------------------------------------------------------

    def read_candidates(self, filepath):

        candidates = []

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                word = line.strip()

                if word:
                    candidates.append(word)

        return candidates

    # --------------------------------------------------------
    # Filter one file
    # --------------------------------------------------------

    def filter_file(
        self,
        filepath,
        category
    ):

        candidates = self.read_candidates(
            filepath
        )

        filtered = []

        for word in candidates:

            if self.filter_candidate(
                word,
                category
            ):

                filtered.append(
                    self.normalize(word)
                )

        # Deduplicate case-insensitively
        unique = {}

        for word in filtered:

            key = word.casefold()

            if key not in unique:
                unique[key] = word

        return sorted(
            unique.values(),
            key=str.casefold
        )

    # --------------------------------------------------------
    # Generate filtered candidates
    # --------------------------------------------------------

    def run_filter(self):

        self.OUTPUT_PATH.mkdir(
            parents=True,
            exist_ok=True
        )

        results = {}

        print("=" * 80)
        print("WordNet Candidate Quality Filtering")
        print("=" * 80)

        print(
            "\nOriginal candidate files are NOT modified."
        )

        print(
            "Filtered files will be written to:"
        )

        print(
            self.OUTPUT_PATH
        )

        for category, config in self.CATEGORY_RULES.items():

            filename = (
                category
                + "_candidates.txt"
            )

            input_file = (
                self.INPUT_PATH
                / filename
            )

            if not input_file.exists():

                print(
                    "\nSkipping missing file:",
                    input_file
                )

                continue

            print(
                "\nProcessing:",
                category
            )

            filtered = self.filter_file(
                input_file,
                category
            )

            output_file = (
                self.OUTPUT_PATH
                / filename
            )

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as f:

                for word in filtered:

                    f.write(
                        word + "\n"
                    )

            results[category] = {
                "input": self.stats[
                    category
                ]["input"],
                "output": len(filtered),
                "removed": (
                    self.stats[
                        category
                    ]["input"]
                    - len(filtered)
                ),
                "file": output_file,
            }

            print(
                "Input candidates :",
                results[category]["input"]
            )

            print(
                "Filtered output  :",
                results[category]["output"]
            )

            print(
                "Removed           :",
                results[category]["removed"]
            )

        return results

    # --------------------------------------------------------
    # Print statistics
    # --------------------------------------------------------

    def print_statistics(self, results):

        print("\n")
        print("=" * 80)
        print("FILTERING SUMMARY")
        print("=" * 80)

        print(
            f"{'CATEGORY':20}"
            f"{'INPUT':>10}"
            f"{'KEPT':>10}"
            f"{'REMOVED':>10}"
        )

        print("-" * 80)

        for category, result in results.items():

            print(
                f"{category:20}"
                f"{result['input']:10}"
                f"{result['output']:10}"
                f"{result['removed']:10}"
            )

    # --------------------------------------------------------
    # Print examples
    # --------------------------------------------------------

    def print_examples(
        self,
        results,
        limit=30
    ):

        print("\n")
        print("=" * 80)
        print("FILTERED CANDIDATE EXAMPLES")
        print("=" * 80)

        for category, result in results.items():

            filepath = result["file"]

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as f:

                words = [
                    line.strip()
                    for line in f
                    if line.strip()
                ]

            print("\n" + "-" * 80)
            print(category.upper())
            print("-" * 80)

            for word in words[:limit]:

                print(
                    " ",
                    word
                )

    # --------------------------------------------------------
    # Save summary
    # --------------------------------------------------------

    def save_summary(self, results):

        filepath = (
            self.OUTPUT_PATH
            / "filter_summary.txt"
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                "WordNet Candidate Filtering Summary\n"
            )

            f.write(
                "=" * 80 + "\n\n"
            )

            f.write(
                "Original candidate files were not modified.\n"
            )

            f.write(
                "Filtered candidates are still NOT accepted entity lists.\n\n"
            )

            for category, result in results.items():

                f.write(
                    f"{category.upper()}\n"
                )

                f.write(
                    f"  Input   : {result['input']}\n"
                )

                f.write(
                    f"  Kept    : {result['output']}\n"
                )

                f.write(
                    f"  Removed : {result['removed']}\n"
                )

                f.write("\n")

        print(
            "\nSummary written to:",
            filepath
        )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    candidate_filter = (
        WordNetCandidateFilter()
    )

    results = (
        candidate_filter.run_filter()
    )

    candidate_filter.print_statistics(
        results
    )

    candidate_filter.print_examples(
        results,
        limit=20
    )

    candidate_filter.save_summary(
        results
    )

    print("\n")
    print("=" * 80)
    print("FILTERING COMPLETE")
    print("=" * 80)
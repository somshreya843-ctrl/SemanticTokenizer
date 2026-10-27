from pathlib import Path
from collections import defaultdict

from nltk.corpus import wordnet as wn


class WordNetCandidateEvidence:

    INPUT_PATH = Path(
        "data/dictionary_candidates/filtered"
    )

    OUTPUT_PATH = Path(
        "data/dictionary_candidates/evidence"
    )

    CATEGORY_MAPPING = {
        "animal": "noun.animal",
        "plant": "noun.plant",
        "person": "noun.person",
        "location": "noun.location",
        "food": "noun.food",
        "body_part": "noun.body",
        "group": "noun.group",
        "attribute": "noun.attribute",
        "concept": "noun.cognition",
        "object": "noun.object",
        "quantity": "noun.quantity",
        "event": "noun.event",
        "possession": "noun.possession",
        "time": "noun.time",
        "phenomenon": "noun.phenomenon",
        "relation": "noun.relation",
        "feeling": "noun.feeling",
        "shape": "noun.shape",
        "motive": "noun.motive",
    }

    # --------------------------------------------------------
    # Read candidates
    # --------------------------------------------------------

    def read_candidates(self, category):

        filepath = (
            self.INPUT_PATH
            / f"{category}_candidates.txt"
        )

        if not filepath.exists():
            return []

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as f:

            return [
                line.strip()
                for line in f
                if line.strip()
            ]

    # --------------------------------------------------------
    # Find WordNet synsets
    # --------------------------------------------------------

    def get_synsets(self, word):

        # WordNet uses underscores for multi-word expressions.
        lookup_word = word.replace(" ", "_")

        return wn.synsets(
            lookup_word,
            pos="n"
        )

    # --------------------------------------------------------
    # Get all semantic categories for a word
    # --------------------------------------------------------

    def get_categories(self, synsets):

        categories = set()

        for synset in synsets:

            # Direct category
            categories.add(
                synset.lexname()
            )

            # Categories encountered through
            # hypernym paths
            for path in synset.hypernym_paths():

                for node in path:

                    lexname = node.lexname()

                    if lexname != "noun.Tops":
                        categories.add(
                            lexname
                        )

        return sorted(categories)

    # --------------------------------------------------------
    # Get hypernym paths
    # --------------------------------------------------------

    def get_paths(self, synsets):

        paths = []

        seen = set()

        for synset in synsets:

            for path in synset.hypernym_paths():

                path_data = []

                for node in path:

                    item = (
                        node.name(),
                        node.lexname()
                    )

                    path_data.append(item)

                key = tuple(path_data)

                if key in seen:
                    continue

                seen.add(key)

                paths.append(
                    path_data
                )

        return paths

    # --------------------------------------------------------
    # Analyze one candidate
    # --------------------------------------------------------

    def analyze_word(
        self,
        word,
        expected_category
    ):

        synsets = self.get_synsets(
            word
        )

        categories = self.get_categories(
            synsets
        )

        evidence = {
            "word": word,
            "expected_category": expected_category,
            "synset_count": len(synsets),
            "categories": categories,
            "matches_expected": (
                expected_category
                in categories
            ),
            "senses": [],
            "paths": self.get_paths(
                synsets
            ),
        }

        for synset in synsets:

            sense = {
                "synset": synset.name(),
                "lexname": synset.lexname(),
                "definition": synset.definition(),
            }

            evidence["senses"].append(
                sense
            )

        return evidence

    # --------------------------------------------------------
    # Calculate confidence
    # --------------------------------------------------------

    @staticmethod
    def calculate_confidence(
        evidence
    ):

        expected = (
            evidence["expected_category"]
        )

        categories = set(
            evidence["categories"]
        )

        synset_count = (
            evidence["synset_count"]
        )

        if synset_count == 0:
            return "NO_WORDNET_SENSE"

        # Expected category is present and
        # no competing semantic category.
        if (
            expected in categories
            and len(categories) == 1
        ):
            return "HIGH"

        # Expected category is present but
        # other categories also exist.
        if expected in categories:
            return "MEDIUM"

        return "LOW"

    # --------------------------------------------------------
    # Generate evidence
    # --------------------------------------------------------

    def generate(self):

        self.OUTPUT_PATH.mkdir(
            parents=True,
            exist_ok=True
        )

        all_results = {}

        print("=" * 80)
        print(
            "WordNet Candidate Evidence Analysis"
        )
        print("=" * 80)

        for category, expected_category in (
            self.CATEGORY_MAPPING.items()
        ):

            candidates = self.read_candidates(
                category
            )

            print(
                f"\nProcessing {category}: "
                f"{len(candidates)} candidates"
            )

            results = []

            for word in candidates:

                evidence = self.analyze_word(
                    word,
                    expected_category
                )

                evidence["confidence"] = (
                    self.calculate_confidence(
                        evidence
                    )
                )

                results.append(
                    evidence
                )

            all_results[category] = results

            self.write_category_report(
                category,
                results
            )

        self.write_summary(
            all_results
        )

        return all_results

    # --------------------------------------------------------
    # Write category report
    # --------------------------------------------------------

    def write_category_report(
        self,
        category,
        results
    ):

        filepath = (
            self.OUTPUT_PATH
            / f"{category}_evidence.txt"
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                "WordNet Candidate Evidence\n"
            )

            f.write(
                "=" * 80 + "\n\n"
            )

            for result in results:

                f.write(
                    f"WORD: "
                    f"{result['word']}\n"
                )

                f.write(
                    f"EXPECTED CATEGORY: "
                    f"{result['expected_category']}\n"
                )

                f.write(
                    f"CONFIDENCE: "
                    f"{result['confidence']}\n"
                )

                f.write(
                    f"NUMBER OF SENSES: "
                    f"{result['synset_count']}\n"
                )

                f.write(
                    "ALL CATEGORIES:\n"
                )

                for category_name in (
                    result["categories"]
                ):

                    f.write(
                        f"  - {category_name}\n"
                    )

                f.write(
                    "\nSENSES:\n"
                )

                for sense in (
                    result["senses"]
                ):

                    f.write(
                        f"  {sense['synset']}\n"
                    )

                    f.write(
                        f"    Lexname: "
                        f"{sense['lexname']}\n"
                    )

                    f.write(
                        f"    Definition: "
                        f"{sense['definition']}\n"
                    )

                f.write(
                    "\nHYPERNYM PATHS:\n"
                )

                for path in result["paths"]:

                    f.write(
                        "  PATH:\n"
                    )

                    for node_name, lexname in path:

                        f.write(
                            f"    "
                            f"{node_name}"
                            f" -> "
                            f"{lexname}\n"
                        )

                f.write(
                    "\n"
                    + "-" * 80
                    + "\n\n"
                )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    def write_summary(
        self,
        all_results
    ):

        filepath = (
            self.OUTPUT_PATH
            / "evidence_summary.txt"
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                "WordNet Candidate Evidence Summary\n"
            )

            f.write(
                "=" * 80 + "\n\n"
            )

            f.write(
                "HIGH = expected category is the "
                "only detected semantic category.\n"
            )

            f.write(
                "MEDIUM = expected category exists "
                "but other categories also exist.\n"
            )

            f.write(
                "LOW = expected category is not "
                "supported by the hierarchy.\n"
            )

            f.write(
                "NO_WORDNET_SENSE = no noun sense found.\n\n"
            )

            for category, results in (
                all_results.items()
            ):

                counts = defaultdict(int)

                for result in results:

                    counts[
                        result["confidence"]
                    ] += 1

                f.write(
                    f"{category.upper()}\n"
                )

                f.write(
                    f"  Total candidates : "
                    f"{len(results)}\n"
                )

                for confidence in [
                    "HIGH",
                    "MEDIUM",
                    "LOW",
                    "NO_WORDNET_SENSE",
                ]:

                    f.write(
                        f"  {confidence:18} : "
                        f"{counts[confidence]}\n"
                    )

                f.write("\n")

    # --------------------------------------------------------
    # Print important examples
    # --------------------------------------------------------

    def print_examples(
        self,
        results,
        limit=10
    ):

        print("\n")
        print("=" * 80)
        print("EVIDENCE EXAMPLES")
        print("=" * 80)

        for category, records in (
            results.items()
        ):

            print(
                f"\n{category.upper()}"
            )

            shown = 0

            for record in records:

                if record["confidence"] not in {
                    "HIGH",
                    "MEDIUM",
                }:
                    continue

                print(
                    "\nWORD:",
                    record["word"]
                )

                print(
                    "CONFIDENCE:",
                    record["confidence"]
                )

                print(
                    "CATEGORIES:",
                    ", ".join(
                        record["categories"]
                    )
                )

                if record["senses"]:

                    print(
                        "DEFINITION:",
                        record["senses"][0][
                            "definition"
                        ]
                    )

                shown += 1

                if shown >= limit:
                    break


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    analyzer = WordNetCandidateEvidence()

    results = analyzer.generate()

    analyzer.print_examples(
        results,
        limit=10
    )

    print("\n")
    print("=" * 80)
    print("EVIDENCE ANALYSIS COMPLETE")
    print("=" * 80)
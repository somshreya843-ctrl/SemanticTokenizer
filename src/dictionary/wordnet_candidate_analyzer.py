from collections import Counter, defaultdict

from nltk.corpus import wordnet as wn


class WordNetCandidateAnalyzer:
    """
    Analyze WordNet noun vocabulary and identify candidate words
    that may represent semantic categories not yet covered by
    the existing SemanticTokenizer entity types.

    IMPORTANT:
    - This script is analysis-only.
    - It does NOT modify existing entity lists.
    - It does NOT automatically create new entity types.
    """

    # --------------------------------------------------------
    # Existing SemanticTokenizer entity types
    # --------------------------------------------------------

    EXISTING_ENTITY_TYPES = {
        "CITY",
        "COUNTRY",
        "STATE",
        "CONTINENT",
        "RIVER",
        "MOUNTAIN",
        "LAKE",
        "ISLAND",
        "FOREST",
        "AIRPORT",
        "RAILWAY_STATION",
        "BRIDGE",
        "DAM",
        "PARK",
        "FARM_EQUIPMENT",
        "MEDICAL_PROCEDURE",
        "DIAGNOSTIC_TEST",
        "VACCINE",
        "PROGRAMMING_LANGUAGE",
        "LANGUAGE",
        "CROP",
        "DISEASE",
        "SYMPTOM",
        "CHEMICAL_ELEMENT",
        "COMPOUND",
        "METAL",
        "NON_METAL",
        "GAS",
        "MINERAL",
        "ACID",
        "BASE",
        "SALT",
        "POLYMER",
        "MEDICINE",
        "FERTILIZER",
        "PESTICIDE",
        "HERBICIDE",
        "NUTRIENT",
        "CURRENCY",
    }

    # --------------------------------------------------------
    # Candidate mappings
    # --------------------------------------------------------

    CATEGORY_CANDIDATE_TYPES = {
        "noun.person": "PERSON",
        "noun.animal": "ANIMAL",
        "noun.plant": "PLANT",
        "noun.location": "LOCATION",
        "noun.attribute": "ATTRIBUTE",
        "noun.cognition": "CONCEPT",
        "noun.group": "GROUP / ORGANIZATION",
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
    # Constructor
    # --------------------------------------------------------

    def __init__(self):
        self.synsets = list(wn.all_synsets(pos="n"))

    # --------------------------------------------------------
    # Normalize WordNet lemma
    # --------------------------------------------------------

    @staticmethod
    def normalize(word):
        """
        Convert WordNet lemma format into readable text.
        """

        return word.replace("_", " ").strip()

    # --------------------------------------------------------
    # Check whether candidate is usable
    # --------------------------------------------------------

    @staticmethod
    def is_valid_candidate(word):
        """
        Basic candidate filtering.

        This is intentionally conservative.
        """

        if not word:
            return False

        if len(word) < 2:
            return False

        if word.isdigit():
            return False

        return True

    # --------------------------------------------------------
    # Get words for a WordNet category
    # --------------------------------------------------------

    def get_words_by_category(self, category):
        """
        Return unique normalized noun lemmas belonging
        directly to a WordNet lexname.
        """

        words = set()

        for synset in self.synsets:

            if synset.lexname() != category:
                continue

            for lemma in synset.lemmas():

                word = self.normalize(lemma.name())

                if self.is_valid_candidate(word):
                    words.add(word)

        return sorted(words, key=str.casefold)

    # --------------------------------------------------------
    # Get semantic categories from hypernym hierarchy
    # --------------------------------------------------------

    def get_hierarchy_categories(self, word):
        """
        Find all WordNet semantic categories encountered
        in the hypernym paths of all noun senses of a word.
        """

        categories = set()

        synsets = wn.synsets(word.replace(" ", "_"), pos="n")

        for synset in synsets:

            for path in synset.hypernym_paths():

                for node in path:

                    category = node.lexname()

                    if category != "noun.Tops":
                        categories.add(category)

        return sorted(categories)

    # --------------------------------------------------------
    # Get candidate records
    # --------------------------------------------------------

    def extract_candidate_records(self):
        """
        Create detailed records for noun candidates.

        Each record contains:
        - word
        - direct WordNet category
        - synset
        - definition
        - hierarchy categories
        """

        records = []

        for synset in self.synsets:

            direct_category = synset.lexname()

            for lemma in synset.lemmas():

                word = self.normalize(lemma.name())

                if not self.is_valid_candidate(word):
                    continue

                hierarchy_categories = set()

                for path in synset.hypernym_paths():

                    for node in path:

                        category = node.lexname()

                        if category != "noun.Tops":
                            hierarchy_categories.add(category)

                records.append(
                    {
                        "word": word,
                        "synset": synset.name(),
                        "direct_category": direct_category,
                        "definition": synset.definition(),
                        "hierarchy_categories": sorted(
                            hierarchy_categories
                        ),
                    }
                )

        return records

    # --------------------------------------------------------
    # Candidate counts
    # --------------------------------------------------------

    def print_candidate_counts(self):
        """
        Print candidate vocabulary size for each
        potentially useful semantic category.
        """

        print("\n")
        print("=" * 80)
        print("WORDNET CANDIDATE VOCABULARY")
        print("=" * 80)

        for category, candidate_type in self.CATEGORY_CANDIDATE_TYPES.items():

            words = self.get_words_by_category(category)

            print(
                f"{category:25}"
                f"=> {len(words):6} words"
                f"  -> candidate: {candidate_type}"
            )

    # --------------------------------------------------------
    # Example candidates
    # --------------------------------------------------------

    def print_examples(self, limit=30):
        """
        Print example words for potentially useful
        new semantic categories.
        """

        print("\n")
        print("=" * 80)
        print("EXAMPLE WORDNET CANDIDATES")
        print("=" * 80)

        for category, candidate_type in self.CATEGORY_CANDIDATE_TYPES.items():

            words = self.get_words_by_category(category)

            print("\n" + "-" * 80)
            print(
                f"{category} -> {candidate_type}"
            )
            print("-" * 80)

            for word in words[:limit]:

                print(" ", word)

    # --------------------------------------------------------
    # Detailed analysis of selected words
    # --------------------------------------------------------

    def analyze_words(self, words):
        """
        Show WordNet senses and semantic hierarchy
        for selected words.
        """

        print("\n")
        print("=" * 80)
        print("WORD-LEVEL SEMANTIC ANALYSIS")
        print("=" * 80)

        for word in words:

            print("\n" + "=" * 80)
            print("WORD:", word)
            print("=" * 80)

            synsets = wn.synsets(
                word.replace(" ", "_"),
                pos="n"
            )

            if not synsets:

                print("No noun synsets found.")

                continue

            for synset in synsets:

                print("\nSYNSET:", synset.name())
                print(
                    "DIRECT CATEGORY:",
                    synset.lexname()
                )

                print(
                    "DEFINITION:",
                    synset.definition()
                )

                print("HYPERNYM CATEGORIES:")

                categories = set()

                for path in synset.hypernym_paths():

                    for node in path:

                        category = node.lexname()

                        if category != "noun.Tops":
                            categories.add(category)

                for category in sorted(categories):

                    print("  ", category)

    # --------------------------------------------------------
    # Build category overlap report
    # --------------------------------------------------------

    def build_overlap_report(self):
        """
        Identify words that appear in multiple WordNet
        noun categories.

        These are important because they demonstrate
        semantic ambiguity.
        """

        word_categories = defaultdict(set)

        for synset in self.synsets:

            category = synset.lexname()

            for lemma in synset.lemmas():

                word = self.normalize(lemma.name())

                if not self.is_valid_candidate(word):
                    continue

                word_categories[word].add(category)

        ambiguous = []

        for word, categories in word_categories.items():

            if len(categories) > 1:

                ambiguous.append(
                    (
                        word,
                        sorted(categories)
                    )
                )

        ambiguous.sort(
            key=lambda x: x[0].casefold()
        )

        return ambiguous

    # --------------------------------------------------------
    # Print overlap examples
    # --------------------------------------------------------

    def print_overlap_examples(self, limit=50):
        """
        Print examples of words belonging to multiple
        WordNet semantic categories.
        """

        ambiguous = self.build_overlap_report()

        print("\n")
        print("=" * 80)
        print("WORDNET SEMANTIC OVERLAP")
        print("=" * 80)

        print(
            f"Total ambiguous words: {len(ambiguous)}"
        )

        print("\nExamples:")

        for word, categories in ambiguous[:limit]:

            print(
                f"  {word} -> "
                f"{', '.join(categories)}"
            )

    # --------------------------------------------------------
    # Main analysis
    # --------------------------------------------------------

    def run(self):

        print("=" * 80)
        print("WordNet Candidate Analysis")
        print("=" * 80)

        print(
            "\nIMPORTANT:"
        )

        print(
            "This is an analysis-only step."
        )

        print(
            "No existing entity lists are modified."
        )

        print(
            "No new entity type is automatically created."
        )

        print(
            f"\nWordNet noun synsets: {len(self.synsets)}"
        )

        # 1. Candidate counts
        self.print_candidate_counts()

        # 2. Example candidates
        self.print_examples(limit=20)

        # 3. Ambiguous vocabulary
        self.print_overlap_examples(limit=50)

        # 4. Important examples
        self.analyze_words(
            [
                "elephant",
                "rose",
                "city",
                "person",
                "car",
                "gold",
                "rice",
                "python",
                "dollar",
            ]
        )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    analyzer = WordNetCandidateAnalyzer()

    analyzer.run()
from collections import Counter
from nltk.corpus import wordnet as wn


class WordNetParser:
    """
    WordNet parser for English dictionary analysis.

    This version:
    - Reads WordNet
    - Extracts noun synsets
    - Analyzes semantic categories
    - Extracts noun records
    - Extracts words by category
    - Produces cleaned noun candidates
    - Analyzes hypernym hierarchy
    - Prints examples from all noun categories

    It does NOT modify the existing entity lists.
    """

    # ========================================================
    # Noun synsets
    # ========================================================

    def get_noun_synsets(self):
        """Return all noun synsets from WordNet."""
        return list(wn.all_synsets(pos="n"))

    # ========================================================
    # Noun statistics
    # ========================================================

    def get_noun_statistics(self):
        """
        Return noun synset counts by WordNet
        semantic category.
        """

        counts = Counter()

        for synset in self.get_noun_synsets():
            counts[synset.lexname()] += 1

        return counts

    # ========================================================
    # Extract noun records
    # ========================================================

    def extract_nouns(self):
        """
        Extract noun lemmas with their WordNet information.

        Each record contains:
        - word
        - synset
        - lexname
        - definition
        """

        records = []

        for synset in self.get_noun_synsets():

            for lemma in synset.lemmas():

                records.append({
                    "word": lemma.name(),
                    "synset": synset.name(),
                    "lexname": synset.lexname(),
                    "definition": synset.definition(),
                })

        return records

    # ========================================================
    # Words by semantic category
    # ========================================================

    def get_words_by_category(self, category):
        """
        Return unique lemma names belonging to a
        specific WordNet semantic category.
        """

        words = set()

        for synset in self.get_noun_synsets():

            if synset.lexname() != category:
                continue

            for lemma in synset.lemmas():

                words.add(lemma.name())

        return sorted(words)

    # ========================================================
    # Clean candidate words
    # ========================================================

    def get_clean_words_by_category(self, category):
        """
        Return normalized candidate words from a
        WordNet noun semantic category.

        Basic filtering:
        - Replace underscores with spaces
        - Remove leading/trailing whitespace
        - Remove empty entries
        - Remove purely numeric entries
        - Ignore single-character entries

        This is only candidate extraction.
        It does NOT classify entities.
        """

        words = set()

        for synset in self.get_noun_synsets():

            if synset.lexname() != category:
                continue

            for lemma in synset.lemmas():

                word = lemma.name().replace("_", " ").strip()

                # Ignore empty entries
                if not word:
                    continue

                # Ignore purely numeric entries
                if word.isdigit():
                    continue

                # Ignore single-character entries
                if len(word) < 2:
                    continue

                words.add(word)

        return sorted(words, key=str.casefold)

    # ========================================================
    # Hierarchy categories
    # ========================================================

    def get_hierarchy_categories(self, word):
        """
        Return all WordNet semantic categories encountered
        in the hypernym paths of the noun senses of a word.
        """

        categories = set()

        synsets = wn.synsets(word, pos="n")

        for synset in synsets:

            for path in synset.hypernym_paths():

                for node in path:

                    lexname = node.lexname()

                    if lexname != "noun.Tops":
                        categories.add(lexname)

        return sorted(categories)

    # ========================================================
    # Print dictionary statistics
    # ========================================================

    def print_statistics(self):

        noun_synsets = self.get_noun_synsets()

        print("=" * 60)
        print("WordNet Dictionary Analysis")
        print("=" * 60)

        print(
            f"Total noun synsets : {len(noun_synsets)}"
        )

        counts = self.get_noun_statistics()

        print(
            "\nNoun synsets by semantic category:"
        )

        print("-" * 60)

        for category, count in counts.most_common():

            print(
                f"{category:30} {count}"
            )

    # ========================================================
    # Print example noun records
    # ========================================================

    def print_examples(self, limit=20):

        records = self.extract_nouns()

        print(
            "\nExample noun records:"
        )

        print("-" * 60)

        for record in records[:limit]:

            print(
                f"{record['word']} | "
                f"{record['synset']} | "
                f"{record['lexname']} | "
                f"{record['definition']}"
            )

    # ========================================================
    # Print selected category examples
    # ========================================================

    def print_category_examples(self, limit=30):

        categories = [
            "noun.animal",
            "noun.plant",
            "noun.location",
            "noun.person",
            "noun.substance",
        ]

        print(
            "\nExample words by category:"
        )

        for category in categories:

            words = self.get_words_by_category(
                category
            )

            print(
                "\n" + "=" * 50
            )

            print(category)

            print(
                "=" * 50
            )

            print(
                "Total unique words:",
                len(words)
            )

            print(
                f"First {limit} words:"
            )

            for word in words[:limit]:

                print(
                    " ",
                    word
                )

    # ========================================================
    # Print clean candidate counts
    # ========================================================

    def print_clean_candidate_counts(self):

        categories = [
            "noun.animal",
            "noun.plant",
            "noun.location",
            "noun.person",
            "noun.substance",
        ]

        print(
            "\nClean candidate counts:"
        )

        print("-" * 60)

        for category in categories:

            words = self.get_clean_words_by_category(
                category
            )

            print(
                f"{category:30} => "
                f"{len(words)} candidates"
            )

    # ========================================================
    # Print hierarchy category analysis
    # ========================================================

    def print_hierarchy_analysis(self):

        test_words = [
            "elephant",
            "rose",
            "city",
            "gold",
            "person",
            "car",
        ]

        print(
            "\nHierarchy category analysis:"
        )

        print(
            "=" * 60
        )

        for word in test_words:

            categories = self.get_hierarchy_categories(
                word
            )

            print(
                f"{word} -> {categories}"
            )

    # ========================================================
    # Print examples from ALL WordNet categories
    # ========================================================

    def print_all_category_examples(self, limit=10):
        """
        Print representative noun examples from every
        WordNet noun semantic category.
        """

        categories = self.get_noun_statistics()

        print(
            "\nWordNet Category Examples"
        )

        print(
            "=" * 70
        )

        for category, count in categories.most_common():

            words = self.get_words_by_category(
                category
            )

            print(
                "\n" + "-" * 70
            )

            print(
                f"{category} | "
                f"{count} noun synsets | "
                f"{len(words)} unique words"
            )

            print(
                "-" * 70
            )

            for word in words[:limit]:

                print(
                    " ",
                    word
                )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    parser = WordNetParser()

    # --------------------------------------------------------
    # 1. Overall noun statistics
    # --------------------------------------------------------

    parser.print_statistics()

    # --------------------------------------------------------
    # 2. Example noun records
    # --------------------------------------------------------

    parser.print_examples()

    # --------------------------------------------------------
    # 3. Examples from selected categories
    # --------------------------------------------------------

    parser.print_category_examples()

    # --------------------------------------------------------
    # 4. Clean candidate counts
    # --------------------------------------------------------

    parser.print_clean_candidate_counts()

    # --------------------------------------------------------
    # 5. Hierarchy category analysis
    # --------------------------------------------------------

    parser.print_hierarchy_analysis()

    # --------------------------------------------------------
    # 6. Examples from ALL WordNet categories
    # --------------------------------------------------------

    parser.print_all_category_examples(
        limit=10
    )
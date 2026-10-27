from nltk.corpus import wordnet as wn


class EntityTypeAnalyzer:
    """
    Analyze representative examples of the existing
    SemanticTokenizer entity types using WordNet.

    This is an analysis-only module.

    It does NOT:
    - modify entity lists
    - create new entity files
    - change the lookup detector
    - change the 19 existing entity types
    """

    # ========================================================
    # Representative examples
    # ========================================================

    TEST_ENTITIES = {

        # Geography
        "CITY": [
            "city",
            "Delhi",
            "London",
        ],

        "COUNTRY": [
            "country",
            "India",
            "France",
        ],

        "STATE": [
            "state",
            "California",
        ],

        "CONTINENT": [
            "continent",
            "Asia",
        ],

        "RIVER": [
            "river",
            "Ganges",
            "Nile",
        ],

        "MOUNTAIN": [
            "mountain",
            "Everest",
        ],

        "LAKE": [
            "lake",
            "Victoria",
        ],

        "ISLAND": [
            "island",
            "Madagascar",
        ],

        "FOREST": [
            "forest",
            "Amazon",
        ],

        "AIRPORT": [
            "airport",
        ],

        "RAILWAY_STATION": [
            "railway station",
        ],

        "BRIDGE": [
            "bridge",
        ],

        "DAM": [
            "dam",
        ],

        "PARK": [
            "park",
        ],

        # Science
        "CHEMICAL_ELEMENT": [
            "oxygen",
            "gold",
        ],

        "COMPOUND": [
            "compound",
        ],

        "METAL": [
            "metal",
            "gold",
        ],

        "NON_METAL": [
            "nonmetal",
        ],

        "GAS": [
            "gas",
            "oxygen",
        ],

        "MINERAL": [
            "mineral",
        ],

        "ACID": [
            "acid",
        ],

        "BASE": [
            "base",
        ],

        "SALT": [
            "salt",
        ],

        "POLYMER": [
            "polymer",
        ],

        # Medicine
        "DISEASE": [
            "disease",
            "diabetes",
        ],

        "MEDICINE": [
            "medicine",
            "paracetamol",
        ],

        "SYMPTOM": [
            "symptom",
            "fever",
        ],

        "MEDICAL_PROCEDURE": [
            "medical procedure",
            "surgery",
        ],

        "DIAGNOSTIC_TEST": [
            "diagnostic test",
            "MRI",
        ],

        "VACCINE": [
            "vaccine",
        ],

        # Technology
        "PROGRAMMING_LANGUAGE": [
            "programming language",
            "Python",
        ],

        # Agriculture
        "CROP": [
            "crop",
            "rice",
        ],

        "FERTILIZER": [
            "fertilizer",
        ],

        "PESTICIDE": [
            "pesticide",
        ],

        "HERBICIDE": [
            "herbicide",
        ],

        "NUTRIENT": [
            "nutrient",
        ],

        "FARM_EQUIPMENT": [
            "farm equipment",
            "tractor",
        ],

        # Language
        "LANGUAGE": [
            "language",
            "English",
        ],

        # Finance
        "CURRENCY": [
            "currency",
            "dollar",
        ],
    }

    # ========================================================
    # Get noun synsets
    # ========================================================

    def get_synsets(self, word):

        return wn.synsets(
            word,
            pos="n"
        )

    # ========================================================
    # Get hypernym paths
    # ========================================================

    def get_paths(self, synset):

        return synset.hypernym_paths()

    # ========================================================
    # Print one entity analysis
    # ========================================================

    def analyze_word(self, word):

        synsets = self.get_synsets(word)

        print("\n" + "=" * 80)
        print("WORD:", word)
        print("NUMBER OF NOUN SENSES:", len(synsets))
        print("=" * 80)

        if not synsets:

            print("No noun synsets found in WordNet.")

            return

        for index, synset in enumerate(synsets, start=1):

            print(
                f"\nSENSE {index}:"
            )

            print(
                "Synset:",
                synset.name()
            )

            print(
                "Lexname:",
                synset.lexname()
            )

            print(
                "Definition:",
                synset.definition()
            )

            print(
                "Hypernym paths:"
            )

            paths = self.get_paths(
                synset
            )

            for path_number, path in enumerate(
                paths,
                start=1
            ):

                print(
                    f"  PATH {path_number}:"
                )

                for node in path:

                    print(
                        f"    {node.name()} "
                        f"=> {node.lexname()}"
                    )

    # ========================================================
    # Analyze all entity types
    # ========================================================

    def analyze_all(self):

        print("=" * 80)
        print(
            "SemanticTokenizer Entity Type "
            "vs WordNet Analysis"
        )
        print("=" * 80)

        for entity_type, words in self.TEST_ENTITIES.items():

            print(
                "\n\n"
                + "#" * 80
            )

            print(
                "ENTITY TYPE:",
                entity_type
            )

            print(
                "#" * 80
            )

            for word in words:

                self.analyze_word(
                    word
                )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    analyzer = EntityTypeAnalyzer()

    analyzer.analyze_all()
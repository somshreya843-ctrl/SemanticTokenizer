from collections import Counter
from nltk.corpus import wordnet as wn


class WordNetCategoryMapper:
    """
    Analyze WordNet noun categories against the existing
    entity types used by SemanticTokenizer.

    IMPORTANT:
    This module is analysis-only.

    It does NOT:
    - modify entity lists
    - add new entity types
    - write files
    - change the lookup detector
    """

    # ========================================================
    # Existing entity types
    # ========================================================

    EXISTING_ENTITY_TYPES = {
        # Geography
        "COUNTRY",
        "CITY",
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
        "DESERT",
        "MONUMENT",
        "OCEAN",
        "VOLCANO",
        "HOSPITAL",
        "MUSEUM",
        "SCHOOL",
        "UNIVERSITY",

        # Agriculture
        "CROP",
        "FARM_EQUIPMENT",
        "FERTILIZER",
        "HERBICIDE",
        "NUTRIENT",
        "PESTICIDE",

        # Business
        "COMPANY",

        # Entertainment
        "ACTOR",
        "BOOK",
        "CINEMATOGRAPHER",
        "COMPOSER",
        "DIRECTOR",
        "EDITOR",
        "MOVIE",
        "PRODUCER",
        "WRITER",

        # Finance
        "CURRENCY",

        # Language
        "LANGUAGE",

        # Medicine
        "DIAGNOSTIC_TEST",
        "DISEASE",
        "MEDICAL_PROCEDURE",
        "MEDICINE",
        "SYMPTOM",
        "VACCINE",

        # Science
        "ACID",
        "BASE",
        "CHEMICAL_ELEMENT",
        "COMPOUND",
        "GAS",
        "METAL",
        "MINERAL",
        "NON_METAL",
        "POLYMER",
        "SALT",

        # Technology
        "PROGRAMMING_LANGUAGE",
    }

    # ========================================================
    # WordNet category -> possible existing entity types
    # ========================================================
    #
    # These are ONLY candidate mappings.
    # They are not automatic classifications.
    #

    CATEGORY_CANDIDATES = {

        "noun.animal": [
            "ANIMAL",
        ],

        "noun.plant": [
            "PLANT",
            "CROP",
        ],

        "noun.person": [
            "PERSON",
        ],

        "noun.location": [
            "LOCATION",
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
        ],

        "noun.substance": [
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
        ],

        "noun.food": [
            "FOOD",
            "CROP",
        ],

        "noun.artifact": [
            "FARM_EQUIPMENT",
            "MEDICAL_PROCEDURE",
            "DIAGNOSTIC_TEST",
        ],

        "noun.body": [
            "BODY_PART",
            "SYMPTOM",
        ],

        "noun.act": [
            "MEDICAL_PROCEDURE",
        ],

        "noun.communication": [
            "LANGUAGE",
            "PROGRAMMING_LANGUAGE",
        ],

        "noun.state": [
            "DISEASE",
            "SYMPTOM",
        ],

        "noun.process": [
            "MEDICAL_PROCEDURE",
        ],

        "noun.phenomenon": [
            "PHENOMENON",
        ],

        "noun.quantity": [
            "QUANTITY",
        ],

        "noun.time": [
            "DATE",
            "TIME",
        ],

        "noun.event": [
            "EVENT",
        ],

        "noun.attribute": [
            "ATTRIBUTE",
        ],

        "noun.group": [
            "ORGANIZATION",
            "GROUP",
        ],

        "noun.cognition": [
            "CONCEPT",
        ],

        "noun.possession": [
            "POSSESSION",
        ],

        "noun.relation": [
            "RELATION",
        ],

        "noun.feeling": [
            "FEELING",
        ],

        "noun.shape": [
            "SHAPE",
        ],

        "noun.object": [
            "OBJECT",
        ],

        "noun.motive": [
            "MOTIVE",
        ],

        "noun.Tops": [
            "ENTITY",
        ],
    }

    # ========================================================
    # Get WordNet noun categories
    # ========================================================

    def get_categories(self):

        categories = Counter()

        for synset in wn.all_synsets(pos="n"):
            categories[synset.lexname()] += 1

        return categories

    # ========================================================
    # Check candidate mapping
    # ========================================================

    def analyze_mapping(self):

        categories = self.get_categories()

        results = []

        for category, count in categories.most_common():

            candidates = self.CATEGORY_CANDIDATES.get(
                category,
                []
            )

            existing = [
                entity_type
                for entity_type in candidates
                if entity_type in self.EXISTING_ENTITY_TYPES
            ]

            new_types = [
                entity_type
                for entity_type in candidates
                if entity_type not in self.EXISTING_ENTITY_TYPES
            ]

            results.append({
                "category": category,
                "synsets": count,
                "existing_types": existing,
                "potential_new_types": new_types,
            })

        return results

    # ========================================================
    # Print mapping analysis
    # ========================================================

    def print_analysis(self):

        results = self.analyze_mapping()

        print("=" * 80)
        print("WordNet → SemanticTokenizer Category Mapping Analysis")
        print("=" * 80)

        print(
            "\nIMPORTANT:"
        )

        print(
            "These mappings are candidate mappings only."
        )

        print(
            "No entity lists or project files are modified."
        )

        for result in results:

            category = result["category"]
            synsets = result["synsets"]
            existing = result["existing_types"]
            new_types = result["potential_new_types"]

            print("\n" + "-" * 80)

            print(
                f"WordNet category : {category}"
            )

            print(
                f"Noun synsets     : {synsets}"
            )

            if existing:

                print(
                    "Existing entity types:"
                )

                for entity_type in existing:

                    print(
                        f"  -> {entity_type}"
                    )

            else:

                print(
                    "Existing entity types:"
                )

                print(
                    "  -> NONE"
                )

            if new_types:

                print(
                    "Potential new entity types:"
                )

                for entity_type in new_types:

                    print(
                        f"  -> {entity_type}"
                    )

            else:

                print(
                    "Potential new entity types:"
                )

                print(
                    "  -> NONE"
                )

    # ========================================================
    # Print categories requiring investigation
    # ========================================================

    def print_investigation_summary(self):

        results = self.analyze_mapping()

        print(
            "\n" + "=" * 80
        )

        print(
            "Categories Requiring Further Investigation"
        )

        print(
            "=" * 80
        )

        print(
            "\nThese categories should NOT be automatically"
        )

        print(
            "converted into entity types yet."
        )

        for result in results:

            category = result["category"]

            existing = result["existing_types"]

            if len(existing) > 1:

                print(
                    f"\n{category}"
                )

                print(
                    "  Multiple possible existing types:"
                )

                for entity_type in existing:

                    print(
                        f"    - {entity_type}"
                    )

    # ========================================================
    # Print potential new categories
    # ========================================================

    def print_new_type_candidates(self):

        results = self.analyze_mapping()

        new_types = set()

        for result in results:

            for entity_type in result[
                "potential_new_types"
            ]:

                new_types.add(entity_type)

        print(
            "\n" + "=" * 80
        )

        print(
            "Potential New Entity Types"
        )

        print(
            "=" * 80
        )

        if not new_types:

            print(
                "\nNo potential new entity types identified."
            )

            return

        for entity_type in sorted(new_types):

            print(
                "  ->",
                entity_type
            )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    mapper = WordNetCategoryMapper()

    # 1. Full mapping analysis
    mapper.print_analysis()

    # 2. Ambiguous mappings
    mapper.print_investigation_summary()

    # 3. Potential new entity types
    mapper.print_new_type_candidates()
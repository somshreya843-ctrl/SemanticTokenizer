class ContextVerifier:
    """
    Verifies lookup entities using context and other detectors.
    """

    CLOSED_TYPES = {

        # ---------------------------------------------------
        # Geography
        # ---------------------------------------------------

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

        # ---------------------------------------------------
        # Science
        # ---------------------------------------------------

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

        # ---------------------------------------------------
        # Medicine
        # ---------------------------------------------------

        "DISEASE",
        "MEDICINE",
        "SYMPTOM",
        "MEDICAL_PROCEDURE",
        "DIAGNOSTIC_TEST",
        "VACCINE",

        # ---------------------------------------------------
        # Technology
        # ---------------------------------------------------

        "PROGRAMMING_LANGUAGE",
        "SOFTWARE",
        "SMARTPHONE",

        # ---------------------------------------------------
        # Agriculture
        # ---------------------------------------------------

        "CROP",
        "FERTILIZER",
        "PESTICIDE",
        "HERBICIDE",
        "NUTRIENT",
        "FARM_EQUIPMENT",

        # ---------------------------------------------------
        # Language
        # ---------------------------------------------------

        "LANGUAGE",

        # ---------------------------------------------------
        # Finance
        # ---------------------------------------------------

        "CURRENCY",
    }

    BAD_PERSON_WORDS = {
        "i", "me", "my", "mine",
        "you", "your",
        "he", "him", "his",
        "she", "her",
        "we", "our",
        "they", "them",
        "it", "its",

        "doctor",
        "teacher",
        "student",
        "farmer",
        "man",
        "woman",
        "boy",
        "girl",
    }

    def verify(
        self,
        regex_entities,
        lookup_entities,
        gliner_entities
    ):

        verified = []

        gliner_spans = {
            (e["start"], e["end"])
            for e in gliner_entities
        }

        # ---------------------------------------------------
        # Verify lookup entities
        # ---------------------------------------------------

        for entity in lookup_entities:

            label = entity["label"].upper()

            # Closed entity types are accepted directly.
            if label in self.CLOSED_TYPES:
                verified.append(entity)
                continue

            # Other lookup entities are accepted only when
            # GLiNER independently detects the same span.
            if (
                entity["start"],
                entity["end"]
            ) in gliner_spans:
                verified.append(entity)

        # ---------------------------------------------------
        # Verify GLiNER entities
        # ---------------------------------------------------

        filtered_gliner = []

        for entity in gliner_entities:

            text = entity["text"].strip().lower()
            label = entity["label"].upper()

            # Reject common words incorrectly detected as PERSON.
            if (
                label == "PERSON"
                and text in self.BAD_PERSON_WORDS
            ):
                continue

            filtered_gliner.append(entity)

        return verified, filtered_gliner
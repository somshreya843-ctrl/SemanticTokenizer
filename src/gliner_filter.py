import re


class GLiNERFilter:

    # -------------------------------------------------------
    # Common occupations that are NOT person names
    # -------------------------------------------------------

    PERSON_BLACKLIST = {
        "doctor",
        "teacher",
        "farmer",
        "student",
        "engineer",
        "scientist",
        "driver",
        "manager",
        "professor",
        "employee",
        "worker",
        "police",
        "police officer",
        "officer",
        "nurse",
        "judge",
        "lawyer",
        "chef",
        "pilot",
        "captain",
        "minister",
        "president",
        "king",
        "queen",
        "actor",
        "actress",
        "director",
        "writer",
        "producer",
        "composer",
        "editor",
    }

    # -------------------------------------------------------
    # Known ambiguous words that should not be PERSON
    # when GLiNER incorrectly assigns PERSON.
    #
    # This is only a temporary safeguard. Context-aware
    # resolution should handle these cases later.
    # -------------------------------------------------------

    NON_PERSON_NAMES = {
        "python",
        "java",
        "gold",
        "amazon",
        "apple",
        "jordan",
    }

    # -------------------------------------------------------
    # Minimum confidence thresholds
    # -------------------------------------------------------

    MIN_SCORE = {
        "PERSON": 0.55,
        "ORGANIZATION": 0.60,
        "LOCATION": 0.60,
        "CITY": 0.60,
        "COUNTRY": 0.60,
        "COMPANY": 0.65,
        "MOVIE": 0.80,
    }

    @classmethod
    def filter(cls, entities):

        filtered = []

        for entity in entities:

            # ------------------------------------------------
            # Basic safety checks
            # ------------------------------------------------

            if not entity:
                continue

            text = entity.get("text", "").strip()

            if not text:
                continue

            label = entity.get("label", "").upper()

            if not label:
                continue

            score = entity.get("score", 1.0)

            # ------------------------------------------------
            # Normalize text for filtering
            # ------------------------------------------------

            normalized = text.casefold()

            # Remove leading articles
            #
            # "The doctor" -> "doctor"
            # "A farmer"   -> "farmer"
            # "An engineer" -> "engineer"
            #

            normalized = re.sub(
                r"^(the|a|an)\s+",
                "",
                normalized
            ).strip()

            # ------------------------------------------------
            # Confidence filtering
            # ------------------------------------------------

            minimum_score = cls.MIN_SCORE.get(
                label,
                0.5
            )

            if score < minimum_score:
                continue

            # ------------------------------------------------
            # Reject punctuation-only predictions
            # ------------------------------------------------

            if re.fullmatch(r"[\W_]+", text):
                continue

            # ------------------------------------------------
            # Reject PERSON occupations
            # ------------------------------------------------

            if (
                label == "PERSON"
                and normalized in cls.PERSON_BLACKLIST
            ):
                continue

            # ------------------------------------------------
            # Reject known non-person words incorrectly
            # classified as PERSON
            # ------------------------------------------------

            if (
                label == "PERSON"
                and normalized in cls.NON_PERSON_NAMES
            ):
                continue

            # ------------------------------------------------
            # Keep valid prediction
            # ------------------------------------------------

            filtered.append(entity)

        return filtered
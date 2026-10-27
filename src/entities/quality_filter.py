import re
from pathlib import Path


class EntityQualityFilter:

    # -------------------------------------------------------
    # Load common stopwords from file
    # -------------------------------------------------------

    STOPWORDS = set()

    stopword_file = Path("data/resources/stopwords.txt")

    if stopword_file.exists():

        with open(stopword_file, "r", encoding="utf-8") as f:

            STOPWORDS = {
                line.strip().lower()
                for line in f
                if line.strip()
            }

    # -------------------------------------------------------
    # Common function words
    # -------------------------------------------------------

    FUNCTION_WORDS = {

        # Articles
        "a", "an", "the",

        # Pronouns
        "i", "me", "my", "mine",
        "you", "your", "yours",
        "he", "him", "his",
        "she", "her", "hers",
        "it", "its",
        "we", "us", "our", "ours",
        "they", "them", "their", "theirs",

        # Auxiliary verbs
        "am", "is", "are", "was", "were",
        "be", "been", "being",
        "do", "does", "did",
        "have", "has", "had",

        # Conjunctions
        "and", "or", "but",

        # Prepositions
        "in", "on", "at", "by",
        "for", "from", "to", "of",
        "with", "into", "onto",
        "over", "under", "between",
        "through", "across", "after",
        "before", "during", "without",
        "within", "against", "among",

        # Determiners
        "this", "that", "these", "those",

        # Miscellaneous
        "as", "if", "then", "than",
    }

    # -------------------------------------------------------
    # Category-specific blacklist
    #
    # These are deliberately category-specific.
    # A word should NOT be removed globally just because
    # it is a common English word.
    # -------------------------------------------------------

    CATEGORY_BLACKLIST = {

        "CITY": {
            "date",
            "salt",
        },

        "RAILWAY_STATION": {
            "bridge",
        },

        "PROGRAMMING_LANGUAGE": {
            "dog",
            "pan",
            "address",
        },

        "NON_METAL": {
            "chemical",
        },
    }

    @classmethod
    def keep(cls, entity: str, category: str = "") -> bool:

        # ---------------------------------------------------
        # Basic validation
        # ---------------------------------------------------

        if entity is None:
            return False

        entity = " ".join(entity.strip().split())

        if not entity:
            return False

        # ---------------------------------------------------
        # Too short
        # ---------------------------------------------------

        if len(entity) < 3:
            return False

        # ---------------------------------------------------
        # Wikidata IDs
        # ---------------------------------------------------

        if re.fullmatch(r"Q\d+", entity):
            return False

        # ---------------------------------------------------
        # Numbers only
        # ---------------------------------------------------

        if entity.isdigit():
            return False

        # ---------------------------------------------------
        # Punctuation only
        # ---------------------------------------------------

        if re.fullmatch(r"[\W_]+", entity):
            return False

        words = entity.casefold().split()

        # ---------------------------------------------------
        # Single stopword
        # ---------------------------------------------------

        if len(words) == 1 and words[0] in cls.STOPWORDS:
            return False

        # ---------------------------------------------------
        # Single function word
        # ---------------------------------------------------

        if len(words) == 1 and words[0] in cls.FUNCTION_WORDS:
            return False

        # ---------------------------------------------------
        # Phrase made entirely of stopwords/function words
        # ---------------------------------------------------

        if all(
            word in cls.STOPWORDS
            or word in cls.FUNCTION_WORDS
            for word in words
        ):
            return False

        # ---------------------------------------------------
        # Reject short title-case function words
        # ---------------------------------------------------

        if (
            len(words) == 1
            and len(entity) <= 5
            and entity[0].isupper()
            and entity[1:].islower()
            and words[0] in cls.FUNCTION_WORDS
        ):
            return False

        # ---------------------------------------------------
        # Category-specific blacklist
        #
        # category comes from filepath.stem in LookupDetector
        # ---------------------------------------------------

        category = category.upper()

        blocked = cls.CATEGORY_BLACKLIST.get(
            category,
            set()
        )

        if entity.casefold() in blocked:
            return False

        # ---------------------------------------------------
        # Keep entity
        # ---------------------------------------------------

        return True
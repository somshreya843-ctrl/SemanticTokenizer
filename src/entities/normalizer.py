import unicodedata


class EntityNormalizer:
    """
    Normalize entity names before validation and writing.
    """

    @staticmethod
    def normalize(entity: str) -> str:

        entity = unicodedata.normalize("NFKC", entity)

        entity = entity.strip()

        entity = " ".join(entity.split())

        return entity
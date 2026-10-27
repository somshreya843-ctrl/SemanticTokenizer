from .normalizer import EntityNormalizer
from .quality_filter import EntityQualityFilter
from .alias_generator import EntityAliasGenerator


class EntityPipeline:
    """
    Complete preprocessing pipeline for entity names.

    Steps:
        1. Normalize
        2. Validate original entity
        3. Generate aliases
        4. Normalize aliases
        5. Validate aliases
        6. Remove duplicates
    """

    @staticmethod
    def process(entity: str, category: str = ""):

        # ----------------------------------------------------
        # Normalize original entity
        # ----------------------------------------------------

        entity = EntityNormalizer.normalize(entity)

        if not entity:
            return []

        # ----------------------------------------------------
        # Validate original entity
        # ----------------------------------------------------

        if not EntityQualityFilter.keep(entity, category):
            return []

        # ----------------------------------------------------
        # Generate aliases
        # ----------------------------------------------------

        aliases = EntityAliasGenerator.generate(entity)

        # Always include the normalized original entity
        aliases.append(entity)

        # ----------------------------------------------------
        # Normalize + Filter + Deduplicate aliases
        # ----------------------------------------------------

        cleaned = []
        seen = set()

        for alias in aliases:

            alias = EntityNormalizer.normalize(alias)

            if not alias:
                continue

            if not EntityQualityFilter.keep(alias, category):
                continue

            key = alias.casefold()

            if key in seen:
                continue

            seen.add(key)
            cleaned.append(alias)

        return cleaned
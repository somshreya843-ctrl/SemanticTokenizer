import re


class EntityAliasGenerator:
    """
    Generate useful aliases from knowledge-base entity names.
    """

    @staticmethod
    def generate(entity: str):

        aliases = {entity}

        ########################################################
        # Remove text inside brackets
        ########################################################

        cleaned = re.sub(
            r"\s*\(.*?\)",
            "",
            entity
        ).strip()

        aliases.add(cleaned)

        ########################################################
        # Remove common suffixes
        ########################################################

        suffixes = [

            "programming language",
            "vaccine",
            "disease",
            "syndrome",
            "virus",
            "river",
            "mountain",
            "lake",
            "airport",
            "international airport",
            "railway station",
            "bridge",
            "national park",
            "chemical element",
            "compound",
            "metal",
            "nonmetal",
            "gas",

        ]

        lower = cleaned.lower()

        for suffix in suffixes:

            if lower.endswith(suffix):

                alias = cleaned[:-len(suffix)].strip()

                if len(alias) >= 2:
                    aliases.add(alias)

        ########################################################
        # Medical abbreviations
        ########################################################

        MEDICAL_ALIASES = {

            "magnetic resonance imaging": {
                "MRI"
            },

            "computed tomography": {
                "CT"
            },

            "computed tomography scan": {
                "CT"
            },

            "electrocardiogram": {
                "ECG",
                "EKG"
            },

            "electroencephalography": {
                "EEG"
            },

            "positron emission tomography": {
                "PET"
            },

            "ultrasound": {
                "USG"
            },

        }

        medical_aliases = MEDICAL_ALIASES.get(
            cleaned.lower(),
            set()
        )

        aliases.update(medical_aliases)

        ########################################################
        # Remove common prefixes
        ########################################################

        prefixes = [

            "the ",
            "city of ",
            "state of ",
            "province of ",

        ]

        lower = cleaned.lower()

        for prefix in prefixes:

            if lower.startswith(prefix):

                alias = cleaned[len(prefix):].strip()

                if len(alias) >= 2:
                    aliases.add(alias)

        ########################################################
        # Collapse multiple spaces
        ########################################################

        final = set()

        for alias in aliases:

            alias = re.sub(
                r"\s+",
                " ",
                alias
            ).strip()

            if alias:
                final.add(alias)

        return sorted(final)
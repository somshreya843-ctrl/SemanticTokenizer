class EntityMerger:

    def __init__(self):

        # Detector priority
        self.priority = {
            "REGEX": 3,
            "GLINER": 2,
            "LOOKUP": 1
        }

        # Normalize labels
        self.label_map = {
            "CITIES": "CITY",
            "COUNTRIES": "COUNTRY",
            "COMPANIES": "COMPANY",
            "MOVIES": "MOVIE"
        }

    def overlap(self, e1, e2):
        """
        Returns True if two entities overlap.
        """
        return not (
            e1["end"] <= e2["start"] or
            e2["end"] <= e1["start"]
        )

    def better_entity(self, old, new):
        """
        Decide which entity to keep.
        """

        # 1. Higher detector priority wins
        if self.priority[new["source"]] > self.priority[old["source"]]:
            return new

        if self.priority[new["source"]] < self.priority[old["source"]]:
            return old

        # 2. Longer entity wins
        old_len = old["end"] - old["start"]
        new_len = new["end"] - new["start"]

        if new_len > old_len:
            return new

        if old_len > new_len:
            return old

        # 3. Higher confidence wins
        old_score = old.get("score", 1.0)
        new_score = new.get("score", 1.0)

        if new_score > old_score:
            return new

        return old

    def merge(self, regex_entities, lookup_entities, gliner_entities):

        merged = []

        # Regex
        for entity in regex_entities:
            entity = entity.copy()
            entity["source"] = "REGEX"
            merged.append(entity)

        # Lookup
        for entity in lookup_entities:
            entity = entity.copy()

            entity["label"] = self.label_map.get(
                entity["label"],
                entity["label"]
            )

            entity["source"] = "LOOKUP"

            merged.append(entity)

        # GLiNER
        for entity in gliner_entities:

            merged.append({
                "text": entity["text"],
                "label": entity["label"].strip().upper().replace(" ", "_"),
                "start": entity["start"],
                "end": entity["end"],
                "score": entity.get("score", 1.0),
                "source": "GLINER"
            })

        ##################################################
        # Resolve duplicates and overlaps
        ##################################################

        final_entities = []

        for entity in merged:

            keep = True

            for i, existing in enumerate(final_entities):

                if self.overlap(entity, existing):

                    best = self.better_entity(existing, entity)

                    final_entities[i] = best

                    keep = False
                    break

            if keep:
                final_entities.append(entity)

        final_entities.sort(key=lambda x: x["start"])

        return final_entities
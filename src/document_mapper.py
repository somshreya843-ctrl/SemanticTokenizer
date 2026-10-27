
class DocumentMapper:
    def __init__(self):
        self.entity_map = {}
        self.counter = {}

    def assign(self, entities):
        mapped_entities = []

        label_map = {
            "PERSON": "<PERSON>",
            "COMPANY": "<ORG>",
            "ORGANIZATION": "<ORG>",
            "CITY": "<LOCATION>",
            "COUNTRY": "<LOCATION>",
            "STATE": "<LOCATION>",
            "LOCATION": "<LOCATION>",
            "EMAIL": "<EMAIL>",
            "PHONE": "<PHONE>",
            "DATE": "<DATE>",
            "URL": "<URL>",
            "IP": "<IP>",
            "PINCODE": "<PINCODE>",
        }

        for original_entity in entities:
            entity = original_entity.copy()
            label = str(
                entity.get("label", "UNKNOWN")
            ).strip().upper().replace(" ", "_")

            if (
                label in {"UNKNOWN", "ENTITY", ""}
                or entity.get("resolution_confidence") == "unresolved"
            ):
                entity["label"] = "UNKNOWN"
                entity["placeholder"] = "<UNKNOWN>"
                entity["resolution_confidence"] = "unresolved"
            else:
                entity["label"] = label
                entity["placeholder"] = label_map.get(
                    label, f"<{label}>"
                )

            mapped_entities.append(entity)

        return mapped_entities

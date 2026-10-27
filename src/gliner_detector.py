from gliner import GLiNER


class GLiNERDetector:

    def __init__(self):

        print("Loading GLiNER model... (first time may take 1-2 minutes)")

        self.model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")

    def detect(self, text):

        labels = [
            "person",
            "organization",
            "location",
            "city",
            "country",
            "company",
            "movie",
            "media format",
        ]


        entities = self.model.predict_entities(
            text,
            labels=labels,
            threshold=0.5
        )

        return entities
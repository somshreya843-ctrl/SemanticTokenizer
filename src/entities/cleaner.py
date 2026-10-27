import re


class EntityCleaner:

    STOPWORDS = {
        "a", "an", "the", "is", "are", "was", "were",
        "in", "on", "at", "of", "to", "for", "by",
        "with", "from", "and", "or", "but",
        "very", "today", "tomorrow", "yesterday",
        "call", "me", "my", "our", "your", "their",
        "this", "that", "these", "those"
    }

    def clean(self, items):

        cleaned = []

        for item in items:

            if not isinstance(item, str):
                continue

            item = item.strip()

            if not item:
                continue

            # Remove text inside brackets
            item = re.sub(r"\s*\(.*?\)", "", item)

            # Remove extra spaces
            item = re.sub(r"\s+", " ", item)

            # Reject very short entities
            if len(item) < 3:
                continue

            # Reject numbers only
            if item.isdigit():
                continue

            # Reject punctuation only
            if not re.search(r"[A-Za-z]", item):
                continue

            # Reject common English words
            if item.lower() in self.STOPWORDS:
                continue

            cleaned.append(item)

        return cleaned
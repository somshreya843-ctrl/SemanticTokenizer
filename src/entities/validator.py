import re


class EntityValidator:

    def validate(self, items):

        valid_items = []

        stopwords = {
            "a", "an", "the", "is", "are", "was", "were",
            "in", "on", "at", "of", "to", "for", "by",
            "with", "and", "or", "from", "my", "your",
            "his", "her", "their", "our", "this", "that",
            "these", "those", "today", "very", "have",
            "has", "had", "be", "been", "being"
        }

        for item in items:

            if not isinstance(item, str):
                continue

            item = item.strip()

            if not item:
                continue

            # Remove entries shorter than 2 characters
            if len(item) < 2:
                continue

            # Reject numbers only
            if item.isdigit():
                continue

            # Reject punctuation-only strings
            if re.fullmatch(r"[\W_]+", item):
                continue

            # Reject common stopwords
            if item.lower() in stopwords:
                continue

            valid_items.append(item)

        return sorted(set(valid_items))
from pathlib import Path


class ContextExtractor:

    def __init__(self, context_window=2):
        """
        context_window:
            Number of surrounding sentences to keep
            on each side of the entity.
        """
        self.context_window = context_window

    def extract_context(
        self,
        text,
        start,
        end
    ):
        """
        Extract local context around an entity occurrence.
        """

        if start < 0 or end > len(text):
            raise ValueError(
                "Invalid entity span."
            )

        entity_text = text[start:end]

        # Find sentence boundaries.
        left_text = text[:start]
        right_text = text[end:]

        left_sentences = self._split_sentences(
            left_text
        )

        right_sentences = self._split_sentences(
            right_text
        )

        current_sentence = (
            self._get_current_sentence(
                text,
                start,
                end
            )
        )

        left_context = left_sentences[
            -self.context_window:
        ]

        right_context = right_sentences[
            :self.context_window
        ]

        context_parts = (
            left_context
            + [current_sentence]
            + right_context
        )

        context = " ".join(
            part.strip()
            for part in context_parts
            if part.strip()
        )

        return {
            "entity": entity_text,
            "start": start,
            "end": end,
            "context": context
        }

    def _split_sentences(self, text):

        if not text.strip():
            return []

        sentences = []

        current = []

        for char in text:

            current.append(char)

            if char in ".!?":

                sentence = "".join(
                    current
                ).strip()

                if sentence:
                    sentences.append(
                        sentence
                    )

                current = []

        remaining = "".join(
            current
        ).strip()

        if remaining:
            sentences.append(
                remaining
            )

        return sentences

    def _get_current_sentence(
        self,
        text,
        start,
        end
    ):

        sentence_start = start

        while sentence_start > 0:

            if text[sentence_start - 1] in ".!?":
                break

            sentence_start -= 1

        sentence_end = end

        while sentence_end < len(text):

            if text[sentence_end] in ".!?":
                sentence_end += 1
                break

            sentence_end += 1

        return text[
            sentence_start:sentence_end
        ].strip()
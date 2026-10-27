
class PlaceholderMapper:
    def replace(self, text, mapped_entities):
        """
        Replace validated entity spans from right to left.
        Invalid and overlapping spans are skipped.
        Original offsets are preserved during replacement.
        """

        validated = []

        # Validate against the ORIGINAL text before making replacements.
        for entity in mapped_entities:
            start = entity.get("start")
            end = entity.get("end")
            entity_text = entity.get("text")
            placeholder = entity.get("placeholder")

            if not isinstance(start, int) or not isinstance(end, int):
                continue

            if not (0 <= start < end <= len(text)):
                continue

            if not isinstance(entity_text, str) or not entity_text:
                continue

            if text[start:end].casefold() != entity_text.casefold():
                print(
                    f"[SKIP_INVALID_SPAN] {entity_text!r} "
                    f"at ({start}, {end})"
                )
                continue

            if not isinstance(placeholder, str) or not placeholder:
                continue

            validated.append({
                "start": start,
                "end": end,
                "text": entity_text,
                "placeholder": placeholder,
            })

        # Resolve overlaps deterministically: keep the longest span first.
        non_overlapping = []
        for entity in sorted(
            validated,
            key=lambda x: (
                -(x["end"] - x["start"]),
                x["start"],
            ),
        ):
            overlaps = any(
                entity["start"] < kept["end"]
                and kept["start"] < entity["end"]
                for kept in non_overlapping
            )
            if not overlaps:
                non_overlapping.append(entity)

        # Replace right to left so earlier offsets remain valid.
        output = text
        for entity in sorted(
            non_overlapping,
            key=lambda x: x["start"],
            reverse=True,
        ):
            output = (
                output[:entity["start"]]
                + entity["placeholder"]
                + output[entity["end"]:]
            )

        return output

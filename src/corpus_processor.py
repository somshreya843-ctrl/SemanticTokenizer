from pathlib import Path
import json
from pydoc import text
import re
import torch

from src.regex_detector import RegexDetector
from src.lookup_detector import LookupDetector
from src.gliner_detector import GLiNERDetector
from src.gliner_filter import GLiNERFilter
from src.ambiguity_resolver import AmbiguityResolver
from src.entity_merger import EntityMerger
from src.document_mapper import DocumentMapper
from src.placeholder_mapper import PlaceholderMapper
from src.context_verifier import ContextVerifier
from src.entities.context_embedder import ContextEmbedder
from src.entities.context_extractor import ContextExtractor


class CorpusProcessor:

    def __init__(
        self,
        grounded_output="data/grounded/entity_sentences.jsonl"
    ):

        self.regex = RegexDetector()
        self.lookup = LookupDetector()
        self.gliner = GLiNERDetector()
        self.verifier = ContextVerifier()
        self.merger = EntityMerger()
        self.placeholder_mapper = PlaceholderMapper()

        self.context_extractor = ContextExtractor(
            context_window=2
        )

        self.context_embedder = ContextEmbedder()

        # -----------------------------------------------------
        # Stage-A grounded output
        # -----------------------------------------------------

        self.grounded_output = Path(
            grounded_output
        )

        self.grounded_output.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    # =========================================================
    # Sentence extraction
    # =========================================================

    @staticmethod
    def _extract_sentence(text, start, end):
        """
        Extract the sentence containing the entity span.
        Return the sentence and its original start offset.
        """
        if start < 0 or end > len(text) or start >= end:
            return "", -1

        left = start
        right = end

        while left > 0 and text[left - 1] not in ".!?":
            left -= 1

        while right < len(text) and text[right] not in ".!?":
            right += 1

        # Include the ending punctuation when present.
        if right < len(text):
            right += 1

        # Remove surrounding whitespace while preserving the true offset.
        while left < right and text[left].isspace():
            left += 1

        while right > left and text[right - 1].isspace():
            right -= 1

        return text[left:right], left

    # =========================================================
    # Stage A: Ground candidate entities in corpus sentences
    # =========================================================

    def _create_grounded_records(
        self,
        text,
        lookup_entities,
        document_name
    ):

        """
        Preserve ALL lookup candidates.

        IMPORTANT:
        No ambiguity resolution is performed here.

        One surface entity may therefore produce multiple
        records with different candidate types.
        """

        records = []

        seen = set()

        for entity in lookup_entities:

            entity_text = entity.get(
                "text",
                ""
            ).strip()

            label = entity.get(
                "label",
                "UNKNOWN"
            ).upper()

            start = int(
                entity.get("start", 0)
            )

            end = int(
                entity.get("end", 0)
            )

            if not entity_text:
                continue

            sentence, sentence_start = self._extract_sentence(
                text,
                start,
                end
            )

            if not sentence or sentence_start < 0:
                continue

            # Convert the original document offset to sentence-relative offset.
            expected_start = start - sentence_start

            # Keep the estimate within the sentence boundaries.
            expected_start = max(0, min(expected_start, len(sentence)))

            # Find all case-insensitive occurrences of the entity.
            matches = list(
                re.finditer(
                    re.escape(entity_text),
                    sentence,
                    re.IGNORECASE
                )
            )

            if not matches:
                continue

            # Prefer the occurrence closest to the detector's estimated offset.
            # Select the occurrence closest to the detector's estimated offset.
            match = min(
                matches,
                key=lambda m: abs(m.start() - expected_start)
)

            # Validate that the detector's original span matches the entity.
            original_span = text[
                int(entity.get("start", 0)):
                int(entity.get("end", 0))
            ]

            if original_span.casefold() != entity_text.casefold():
                # The original detector span is unreliable.
                # Do not silently guess which occurrence was intended.
                continue

            # The original span is valid; use its sentence-relative offsets.
            start = start - sentence_start
            end = start + len(entity_text)

            # -------------------------------------------------
            # Preserve duplicate candidate types only once
            # per occurrence.
            # -------------------------------------------------

            key = (
                document_name,
                start,
                end,
                entity_text.casefold(),
                label,
                sentence
            )

            if key in seen:
                continue

            seen.add(key)

            records.append(
                {
                    "entity": entity_text,
                    "type": label,
                    "sentence": sentence,
                    "start": start,
                    "end": end,
                    "document": document_name
                }
            )

        return records

    # =========================================================
    # Save Stage-A records
    # =========================================================

    def _save_grounded_records(
        self,
        records
    ):

        if not records:
            return

        with open(
            self.grounded_output,
            "a",
            encoding="utf-8"
        ) as f:

            for record in records:

                f.write(
                    json.dumps(
                        record,
                        ensure_ascii=False
                    )
                    + "\n"
                )

    # =========================================================
    # Main document processing
    # =========================================================

    
    def process_document(
        self,
        text,
        document_name="unknown.txt",
        terminal_only=False
    ):
        document_mapper = DocumentMapper()

        # -----------------------------------------------------
        # 1. Detection
        # -----------------------------------------------------
        regex_entities = self.regex.detect(text)

        lookup_entities = self.lookup.detect(text)

        gliner_entities = self.gliner.detect(text)
        gliner_entities = GLiNERFilter.filter(gliner_entities)

        # -----------------------------------------------------
        # 2. Verification
        # -----------------------------------------------------
        verified_lookup, verified_gliner = self.verifier.verify(
            regex_entities,
            lookup_entities,
            gliner_entities
        )

        # -----------------------------------------------------
        # 3. Grounding
        # Write grounded records only in normal processing mode.
        # -----------------------------------------------------
        if not terminal_only:
            grounded_records = self._create_grounded_records(
                text=text,
                lookup_entities=verified_lookup,
                document_name=document_name
            )
            self._save_grounded_records(grounded_records)

        # -----------------------------------------------------
        # 4. Context-based ambiguity resolution
        # -----------------------------------------------------
        resolved_lookup = AmbiguityResolver.resolve(
            text,
            verified_lookup
        )

        # Remember unresolved lookup spans so another detector
        # cannot silently assign a different type to that span.
        unresolved_spans = []

        for entity in resolved_lookup:
            label = str(entity.get("label", "UNKNOWN")).upper()
            confidence_status = entity.get("resolution_confidence")

            if (
                label == "UNKNOWN"
                or confidence_status == "unresolved"
            ):
                unresolved_spans.append({
                    "start": entity.get("start"),
                    "end": entity.get("end"),
                    "text": entity.get("text", ""),
                    "candidate_labels": entity.get(
                        "candidate_labels", [label]
                    ),
                })

        # -----------------------------------------------------
        # 5. Merge detector outputs
        # -----------------------------------------------------
        merged_entities = self.merger.merge(
            regex_entities,
            resolved_lookup,
            verified_gliner
        )

        # Preserve unresolved lookup decisions when overlapping
        # non-regex detections would otherwise assign another type.
        for entity in merged_entities:
            if entity.get("source") == "REGEX":
                continue

            for unresolved in unresolved_spans:
                same_span = (
                    entity.get("start") == unresolved["start"]
                    and entity.get("end") == unresolved["end"]
                )

                if same_span:
                    entity["label"] = "UNKNOWN"
                    entity["resolution_confidence"] = "unresolved"
                    entity["candidate_labels"] = (
                        unresolved["candidate_labels"]
                    )
                    break

        # -----------------------------------------------------
        # 6. Validate exact character spans
        # -----------------------------------------------------
        validated_entities = []

        for entity in merged_entities:
            entity = dict(entity)

            start = entity.get("start")
            end = entity.get("end")
            entity_text = entity.get("text", "")

            valid_span = (
                isinstance(start, int)
                and isinstance(end, int)
                and 0 <= start < end <= len(text)
                and bool(entity_text)
                and text[start:end].casefold()
                    == entity_text.casefold()
            )

            if not valid_span:
                if terminal_only:
                    print(
                        "[INVALID_SPAN] "
                        f"Entity={entity_text!r}, "
                        f"start={start}, end={end}"
                    )
                continue

            validated_entities.append(entity)

        # -----------------------------------------------------
        # 7. Assign safe placeholders
        # -----------------------------------------------------
        mapped_entities = document_mapper.assign(
            validated_entities
        )

        # -----------------------------------------------------
        # 8. Terminal-only evaluation
        # No anonymized text is generated or written to a file.
        # No embedding computation is performed in this mode.
        # -----------------------------------------------------
        if terminal_only:
            print("\n" + "=" * 72)
            print(f"TERMINAL-ONLY ENTITY TEST: {document_name}")
            print("=" * 72)

            for entity in sorted(
                mapped_entities,
                key=lambda item: (
                    item["start"],
                    item["end"]
                )
            ):
                start = entity["start"]
                end = entity["end"]
                entity_text = entity["text"]
                label = entity.get("label", "UNKNOWN")

                valid_span = (
                    0 <= start < end <= len(text)
                    and text[start:end].casefold()
                        == entity_text.casefold()
                )

                unresolved = (
                    label == "UNKNOWN"
                    or entity.get("resolution_confidence")
                        == "unresolved"
                )

                if not valid_span:
                    status = "INVALID_SPAN"
                    proposed = "<UNKNOWN>"
                elif unresolved:
                    status = "UNKNOWN"
                    proposed = "<UNKNOWN>"
                else:
                    status = "CANDIDATE"
                    proposed = entity.get(
                        "placeholder", "<UNKNOWN>"
                    )

                print(f"\nOriginal entity : {entity_text!r}")
                print(f"Original context: {text[max(0, start - 60):min(len(text), end + 60)]!r}")
                print(f"Resolved type   : {label}")
                print(f"Status          : {status}")
                print(f"Offsets         : ({start}, {end})")
                print(f"Proposed token  : {proposed}")

            print("\n" + "=" * 72)
            print("Terminal-only test complete; no corpus output written.")
            print("=" * 72)

            return text, mapped_entities, []

        # -----------------------------------------------------
        # 9. Normal processing mode
        # -----------------------------------------------------
        contextual_entities = []

        for entity in mapped_entities:
            context_info = self.context_extractor.extract_context(
                text,
                entity["start"],
                entity["end"]
            )

            enriched_entity = dict(entity)
            enriched_entity["context"] = context_info["context"]
            enriched_entity["category"] = entity.get(
                "category",
                entity.get("label", "UNKNOWN")
            )

            contextual_entities.append(enriched_entity)

        embedded_entities = self.context_embedder.encode_entities(
            text,
            contextual_entities
        )

        semantic_text = self.placeholder_mapper.replace(
            text,
            mapped_entities
        )

        return (
            semantic_text,
            contextual_entities,
            embedded_entities
        )

    # =========================================================
    # Process corpus folder
    # =========================================================

    def process_folder(
        self,
        input_folder,
        output_folder
    ):

        input_folder = Path(
            input_folder
        )

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        txt_files = sorted(
            input_folder.glob("*.txt")
        )

        print(
            f"Found {len(txt_files)} corpus files."
        )

        for file in txt_files:

            print(
                f"Processing {file.name}"
            )

            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:

                text = f.read()

            (
                semantic_text,
                entity_map,
                embedded_entities
            ) = self.process_document(
                text,
                document_name=file.name
            )

            output_file = (
                output_folder / file.name
            )

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    semantic_text
                )

            print("  Stage-A grounding completed.")
            
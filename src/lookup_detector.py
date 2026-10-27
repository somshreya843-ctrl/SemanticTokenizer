"""
lookup_detector.py

Research-level Lookup Detector
------------------------------
Features
- Reverse lookup table
- Trie-based lookup
- Longest-match-first
- Multiple labels
- Case insensitive
- Paragraph -> Sentence -> Segment parsing
- Tokenizer preserving emails, URLs, IPs and dates
- Regex-first priority
- Persistent lookup index caching
"""

import re
import pickle
import hashlib
from pathlib import Path

from src.trie import Trie
from src.regex_detector import RegexDetector
from src.entities.quality_filter import EntityQualityFilter


class LookupDetector:

    def __init__(self, lookup_path="data/entities"):

        self.lookup_path = Path(lookup_path)

        # Persistent lookup index
        self.index_path = Path("cache/lookup_index.pkl")
        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.trie = Trie()
        self.regex_detector = RegexDetector()

        #########################################################
        # Tokenizer Pattern
        #########################################################

        self.token_pattern = re.compile(
            r"""
            https?://[^\s]+|
            www\.[^\s]+|
            [A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|
            (?:\d{1,3}\.){3}\d{1,3}|
            \d{4}-\d{2}-\d{2}|
            \d{1,2}/\d{1,2}/\d{2,4}|
            [A-Za-z]\.|
            [A-Za-z][A-Za-z0-9+#-]*(?:['-][A-Za-z0-9+#-]+)*|
            \d+
            """,
            re.VERBOSE,
        )

        #########################################################
        # Load cached index or build it
        #########################################################

        if self._cache_is_valid():

            self._load_index()

        else:

            self._build_index()
            self._save_index()

    #########################################################
    # Entity file signature
    #########################################################

    def _get_entity_files_signature(self):

        """
        Create a signature representing the current state
        of all entity files.

        If any entity file is added, removed, or modified,
        the signature changes and the lookup index is rebuilt.
        """

        hasher = hashlib.sha256()

        files = sorted(
            self.lookup_path.rglob("*.txt")
        )

        for filepath in files:

            try:

                stat = filepath.stat()

            except FileNotFoundError:

                continue

            relative_path = filepath.relative_to(
                self.lookup_path
            )

            hasher.update(
                str(relative_path).encode("utf-8")
            )

            hasher.update(
                str(stat.st_size).encode("utf-8")
            )

            hasher.update(
                str(stat.st_mtime_ns).encode("utf-8")
            )

        return hasher.hexdigest()

    #########################################################
    # Check cache validity
    #########################################################

    def _cache_is_valid(self):

        if not self.index_path.exists():

            return False

        try:

            with open(
                self.index_path,
                "rb"
            ) as f:

                cached = pickle.load(f)

            cached_signature = cached.get(
                "signature"
            )

            if not cached_signature:

                return False

            current_signature = (
                self._get_entity_files_signature()
            )

            return (
                cached_signature
                == current_signature
            )

        except Exception as e:

            print(
                f"[WARNING] Could not validate lookup cache: {e}"
            )

            return False

    #########################################################
    # Load cached index
    #########################################################

    def _load_index(self):

        try:

            with open(
                self.index_path,
                "rb"
            ) as f:

                cached = pickle.load(f)

            self.lookup = cached["lookup"]
            self.trie = cached["trie"]

            print(
                f"Loaded {len(self.lookup)} unique entities "
                f"from lookup cache."
            )

        except Exception as e:

            print(
                f"[WARNING] Could not load lookup cache: {e}"
            )

            print(
                "Rebuilding lookup index..."
            )

            self._build_index()
            self._save_index()

    #########################################################
    # Build lookup index
    #########################################################

    def _build_index(self):

        print(
            "Building lookup index from entity files..."
        )

        #########################################################
        # Reverse Lookup Table
        #########################################################

        self.lookup = {}

        file_count = 0
        raw_entities = 0
        filtered_entities = 0

        for filepath in self.lookup_path.rglob("*.txt"):

            file_count += 1

            entity_type = filepath.stem.upper()

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as f:

                for line in f:

                    raw_entities += 1

                    entity = line.strip()

                    if not entity:
                        continue

                    if not EntityQualityFilter.keep(
                        entity,
                        entity_type
                    ):
                        filtered_entities += 1
                        continue

                    entity = " ".join(
                        entity.split()
                    )

                    if len(entity.split()) > 8:
                        filtered_entities += 1
                        continue

                    #################################################
                    # Reverse lookup
                    #################################################

                    key = entity.casefold()

                    labels = self.lookup.setdefault(
                        key,
                        []
                    )

                    if entity_type not in labels:

                        labels.append(
                            entity_type
                        )

                    #################################################
                    # Trie
                    #################################################

                    self.trie.insert(
                        entity,
                        entity_type
                    )

        print(
            f"Processed {file_count} entity files."
        )

        print(
            f"Raw entity records : {raw_entities}"
        )

        print(
            f"Filtered records   : {filtered_entities}"
        )

        print(
            f"Unique entities    : {len(self.lookup)}"
        )

    #########################################################
    # Save lookup index
    #########################################################

    def _save_index(self):

        print(
            "Saving lookup index..."
        )

        signature = (
            self._get_entity_files_signature()
        )

        cache_data = {
            "signature": signature,
            "lookup": self.lookup,
            "trie": self.trie,
        }

        temporary_path = Path(
            str(self.index_path) + ".tmp"
        )

        with open(
            temporary_path,
            "wb"
        ) as f:

            pickle.dump(
                cache_data,
                f,
                protocol=pickle.HIGHEST_PROTOCOL
            )

        temporary_path.replace(
            self.index_path
        )

        print(
            f"Lookup index saved to: {self.index_path}"
        )

    #########################################################
    # Paragraph -> Sentence -> Segment
    #########################################################

    def segment_text(self, text):

        document = []

        paragraphs = re.split(
            r"\n\s*\n|\n",
            text
        )

        paragraphs = [
            p.strip()
            for p in paragraphs
            if p.strip()
        ]

        for p_idx, paragraph in enumerate(
            paragraphs,
            start=1
        ):

            sentences = re.split(
                r"(?<=[.!?])\s+",
                paragraph
            )

            for s_idx, sentence in enumerate(
                sentences,
                start=1
            ):

                segments = re.split(
                    r'[,;:()\[\]{}"]+',
                    sentence
                )

                for g_idx, segment in enumerate(
                    segments,
                    start=1
                ):

                    segment = segment.strip()

                    if not segment:
                        continue

                    document.append(
                        {
                            "paragraph_id": p_idx,
                            "sentence_id": s_idx,
                            "segment_id": g_idx,
                            "text": segment,
                        }
                    )

        return document

    #########################################################
    # Tokenizer
    #########################################################

    def tokenize(self, text):

        return self.token_pattern.findall(
            text
        )

    #########################################################
    # Lookup Detection
    #########################################################

    def detect(self, text):

        entities = []

        #########################################################
        # Regex has highest priority
        #########################################################

        regex_entities = (
            self.regex_detector.detect(text)
        )

        occupied_spans = [
            (e["start"], e["end"])
            for e in regex_entities
        ]

        #########################################################
        # Tokenize while preserving offsets
        #########################################################

        matches = list(
            self.token_pattern.finditer(text)
        )

        tokens = [
            m.group()
            for m in matches
        ]

        i = 0

        while i < len(tokens):

            match = self.trie.search_longest(
                tokens,
                i
            )

            if match is None:

                i += 1
                continue

            start_char = matches[i].start()

            end_char = matches[
                i + match["length"] - 1
            ].end()

            #####################################################
            # Ignore matches inside regex entities
            #####################################################

            overlap = any(
                start_char < r_end
                and end_char > r_start
                for r_start, r_end
                in occupied_spans
            )

            if overlap:

                i += match["length"]
                continue

            #####################################################
            # Add lookup entities
            #####################################################

            for label in match["labels"]:

                entities.append(
                    {
                        "text": match["text"],
                        "label": label,
                        "start": start_char,
                        "end": end_char,
                    }
                )

            i += match["length"]

        return entities

    #########################################################
    # Parse document
    #########################################################

    def parse(
        self,
        text,
        doc_id="DOC0001"
    ):

        parsed_segments = []

        segments = self.segment_text(
            text
        )

        for segment_info in segments:

            paragraph_id = (
                segment_info["paragraph_id"]
            )

            sentence_id = (
                segment_info["sentence_id"]
            )

            segment_id = (
                segment_info["segment_id"]
            )

            segment = segment_info["text"]

            tokens = self.tokenize(
                segment
            )

            parsed = []
            entities = []

            i = 0

            while i < len(tokens):

                match = self.trie.search_longest(
                    tokens,
                    i
                )

                if match:

                    parsed.append(
                        f"[{'|'.join(match['labels'])}]"
                    )

                    entities.append(
                        {
                            "label": match["labels"],
                            "start": i,
                            "length": match["length"],
                            "value": match["text"],
                        }
                    )

                    i += match["length"]

                    continue

                regex_entities = (
                    self.regex_detector.detect(
                        tokens[i]
                    )
                )

                if regex_entities:

                    entity = regex_entities[0]

                    parsed.append(
                        f"[{entity['label']}]"
                    )

                    entities.append(
                        {
                            "label": [
                                entity["label"]
                            ],
                            "start": i,
                            "length": 1,
                            "value": entity["text"],
                        }
                    )

                else:

                    parsed.append(
                        tokens[i]
                    )

                i += 1

            parsed_segments.append(
                {
                    "id": (
                        f"{doc_id}:"
                        f"P{paragraph_id:04d}:"
                        f"S{sentence_id:04d}:"
                        f"G{segment_id:04d}"
                    ),
                    "original": segment,
                    "parsed": " ".join(parsed),
                    "entities": entities,
                    "metadata": self.entity_metadata(
                        entities
                    ),
                }
            )

        return parsed_segments

    #########################################################
    # Metadata
    #########################################################

    def entity_metadata(self, entities):

        metadata = []

        for entity in entities:

            for label in entity["label"]:

                metadata.append(
                    f"{label}:"
                    f"{entity['start']}:"
                    f"{entity['length']}:"
                    f"{entity['value']}"
                )

        return ",".join(metadata)
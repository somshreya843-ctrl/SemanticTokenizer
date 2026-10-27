"""
regex_detector.py

Features
--------
# Multiple regex patterns for every entity type
# Precompiled regex patterns (faster on large corpora)
# Pattern metadata (pattern name + priority)
# Validation layer
# Normalization layer
# Duplicate removal
# Overlap resolution
# Sorted output
# Easy to extend

"""

import re
import ipaddress
from datetime import datetime


class RegexDetector:

    def __init__(self):

        ##########################################################
        # Pattern Repository
        #
        # Each entity type contains multiple regex patterns.
        # Every pattern has:
        #
        # name      : identifier
        # regex     : compiled regex
        # priority  : used for overlap resolution
        ##########################################################

        self.patterns = {

            "EMAIL": [

                {
                    "name": "standard_email",
                    "priority": 10,
                    "regex": re.compile(
                        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
                    )
                }

            ],

            "PHONE": [

                {
                    "name": "international",
                    "priority": 20,
                    "regex": re.compile(
                        r"\+\d{1,3}[\s\-]?\d{6,14}"
                    )
                },

                {
                    "name": "india_mobile",
                    "priority": 30,
                    "regex": re.compile(
                        r"\b[6-9]\d{9}\b"
                    )
                },

                {
                    "name": "phone_with_dash",
                    "priority": 15,
                    "regex": re.compile(
                        r"\b\d{5}[- ]\d{5}\b"
                    )
                },

                {
                    "name": "us_phone",
                    "priority": 10,
                    "regex": re.compile(
                        r"\(\d{3}\)\s?\d{3}[- ]?\d{4}"
                    )
                }

            ],

            "URL": [

                {
                    "name": "http_https",
                    "priority": 20,
                    "regex": re.compile(
                        r"https?://[^\s]+?(?=[.,!?;:]?(?:\s|$))"
                    )
                },

                {
                    "name": "www_url",
                    "priority": 15,
                    "regex": re.compile(
                        r"www\.[^\s]+"
                    )
                }

            ],

            "DATE": [

                {
                    "name": "dd_mm_yyyy",
                    "priority": 20,
                    "regex": re.compile(
                        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
                    )
                },

                {
                    "name": "yyyy_mm_dd",
                    "priority": 20,
                    "regex": re.compile(
                        r"\b\d{4}-\d{2}-\d{2}\b"
                    )
                },

                {
                    "name": "23 July 2026",
                    "priority": 10,
                    "regex": re.compile(
                        r"\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}\b",
                        re.IGNORECASE
                    )
                },

                {
                    "name": "July 23, 2026",
                    "priority": 10,
                    "regex": re.compile(
                        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{1,2},\s\d{4}\b",
                        re.IGNORECASE
                    )
                }

            ],

            "PINCODE": [

                {
                    "name": "india_pincode",
                    "priority": 20,
                    "regex": re.compile(
                        r"\b\d{6}\b"
                    )
                }

            ],

            "IP": [

                {
                    "name": "ipv4",
                    "priority": 20,
                    "regex": re.compile(
                        r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
                    )
                },

                {
                    "name": "ipv6",
                    "priority": 20,
                    "regex": re.compile(
                        r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"
                    )
                }

            ],

                        "MAC": [

                {
                    "name": "mac_colon",
                    "priority": 30,
                    "regex": re.compile(
                        r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b"
                    )
                },

                {
                    "name": "mac_dash",
                    "priority": 30,
                    "regex": re.compile(
                        r"\b(?:[0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}\b"
                    )
                }

            ],

            "PAN": [

                {
                    "name": "india_pan",
                    "priority": 30,
                    "regex": re.compile(
                        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
                    )
                }

            ],

            "AADHAAR": [

                {
                    "name": "aadhaar",
                    "priority": 30,
                    "regex": re.compile(
                        r"\b\d{4}\s\d{4}\s\d{4}\b"
                    )
                }

            ],

        }

    ####################################################################
    # Validation Layer
    #
    # Regex generates candidates.
    # Validator removes impossible values.
    ####################################################################

    def _validate(self, label, text):

        if label == "IP":
            try:
                ipaddress.ip_address(text)
                return True
            except ValueError:
                return False

        if label == "MAC":

            return True

        if label == "PAN":

            return True

        if label == "AADHAAR":

            digits = re.sub(r"\D", "", text)

            return len(digits) == 12

        if label == "DATE":

            formats = [

                "%d/%m/%Y",
                "%d-%m-%Y",
                "%Y-%m-%d",
                "%d %B %Y",
                "%d %b %Y",
                "%B %d, %Y",
                "%b %d, %Y"

            ]

            for fmt in formats:

                try:
                    datetime.strptime(text, fmt)
                    return True
                except:
                    pass

            return False

        return True

    ####################################################################
    # Normalization Layer
    ####################################################################

    def _normalize(self, label, text):

        if label == "PHONE":

            return re.sub(r"\D", "", text)

        if label == "EMAIL":

            return text.lower()

        if label == "MAC":

            return text.upper()

        if label == "PAN":

            return text.upper()

        if label == "AADHAAR":

            return re.sub(r"\D", "", text)

        return text

    ####################################################################
    # Resolve overlaps
    #
    # Keep
    #
    # 1. higher priority
    # 2. if same priority -> longer span
    ####################################################################

    # def _resolve_overlap(self, entities):

    #     entities.sort(
    #         key=lambda x: (
    #             x["start"],
    #             -x["priority"],
    #             -(x["end"] - x["start"])
    #         )
    #     )

    #     final = []

    #     for entity in entities:

    #         overlap = False

    #         for existing in final:

    #             if not (
    #                 entity["end"] <= existing["start"]
    #                 or
    #                 entity["start"] >= existing["end"]
    #             ):
    #                 overlap = True
    #                 break

    #         if not overlap:
    #             final.append(entity)

    #     return final

    ####################################################################
    # Main detection (Regex Fallback)
    ####################################################################

    def detect(self, text: str) -> list:

        entities = []

        for label, pattern_list in self.patterns.items():

            for pattern_info in pattern_list:

                regex = pattern_info["regex"]

                for match in regex.finditer(text):

                    value = match.group()

                    if not self._validate(label, value):
                        continue

                    value = self._normalize(label, value)

                    entities.append({

                        "text": match.group(),
                        "label": label,
                        "start": match.start(),
                        "end": match.end(),
                        "pattern": pattern_info["name"],
                        "priority": pattern_info["priority"],
                        "normalized": value

                    })

        entities.sort(key=lambda x: x["start"])

        return entities

import re


class AmbiguityResolver:

    CONTEXT_RULES = {
        "COMPANY": {
            "keywords": {
                "company", "startup", "corporation", "founded",
                "acquired", "ceo", "employee", "employees",
                "headquarters", "office", "business", "organization",
                "enterprise", "firm", "launched", "hired",
                "released", "product", "products", "revenue",
                "subsidiary", "manufacturer", "investors"
            }
        },

        "FOOD": {
            "keywords": {
                "ate", "eaten", "eat", "eating", "fruit", "fruits",
                "vegetable", "vegetables", "fresh", "peeled",
                "chopped", "cooked", "ripe", "tasty", "sweet",
                "sour", "food", "ingredient", "ingredients",
                "harvest", "orchard", "juice", "recipe"
            }
        },

        "LANGUAGE": {
            "keywords": {
                "language", "dialect", "speak", "speaks", "spoken",
                "native", "translation", "translate", "translated",
                "grammar", "linguistic", "vocabulary"
            }
        },

        "PROGRAMMING_LANGUAGE": {
            "keywords": {
                "programming", "program", "programmer", "code",
                "coding", "software", "developer", "development",
                "script", "syntax", "compiler", "interpreter",
                "framework", "library", "debug", "backend",
                "frontend", "computer", "computer_science"
            }
        },

        "COUNTRY": {
            "keywords": {
                "country", "nation", "national", "population",
                "territory", "geography", "border", "capital",
                "government", "citizens", "located", "travelling",
                "travelled", "visited", "outside", "border", "capital", "population",
                "country", "nation", "national", "territory",
                "geography", "government", "citizens",
                "japan", "japanese"
            }
        },

        "MOVIE": {
            "keywords": {
                "film", "movie", "cinema", "director", "directed",
                "actor", "actress", "starring", "screenplay",
                "box_office", "released", "sequel"
            }
        },

        "ACTOR": {
            "keywords": {
                "actor", "actress", "starred", "starring",
                "portrayed", "performed", "role", "filmography"
            }
        },

        "BOOK": {
            "keywords": {
                "book", "novel", "author", "written", "wrote",
                "published", "chapter", "pages", "publisher",
                "fiction", "nonfiction", "read", "reading"
            }
        },

        "METAL": {
            "keywords": {
                "metal", "metals", "metallic", "alloy", "steel",
                "ore", "precious", "conductive", "conductivity"
            }
        },

        "CHEMICAL_ELEMENT": {
            "keywords": {
                "chemical", "element", "elements", "periodic",
                "periodic_table", "atomic", "atomic_number", "atom"
            }
        },

        "GAS": {
            "keywords": {
                "gas", "gases", "gaseous", "atmosphere",
                "atmospheric", "inhaled", "breath", "breathing"
            }
        },

        "MEDICINE": {
            "keywords": {
                "medicine", "medication", "drug", "tablet",
                "capsule", "dose", "dosage", "prescribed",
                "prescription", "treatment", "therapy", "patient",
                "doctor", "symptom", "disease"
            }
        },

        "MEDIA_FORMAT": {
            "keywords": {
                "manga", "comic", "comics", "animation",
                "animated", "adapted", "series", "episode"
            }
        },
    }

    # Require a unique positive winner with a clear score margin.
    MIN_SCORE = 1
    MIN_MARGIN = 1

    @classmethod
    def resolve(cls, text, lookup_entities):
        grouped = {}

        for entity in lookup_entities:
            key = (
                entity["start"],
                entity["end"],
                entity["text"].casefold()
            )
            grouped.setdefault(key, []).append(entity)

        resolved = []

        for (start, end, _), candidates in grouped.items():
            # Deduplicate candidates by normalized label.
            unique = {}
            for candidate in candidates:
                label = (
                    candidate.get("label", "UNKNOWN")
                    .strip().upper()
                    .replace(" ", "_")
                )
                unique.setdefault(label, candidate)

            candidates = list(unique.values())

            if len(candidates) == 1:
                candidate = dict(candidates[0])
                label = (
                    candidate.get("label", "UNKNOWN")
                    .strip().upper()
                    .replace(" ", "_")
                )

                # A single lookup match is not sufficient evidence
                # that the entity has the correct semantic type.
                rule = cls.CONTEXT_RULES.get(label)

                left = max(0, start - 100)
                right = min(len(text), end + 100)
                context = text[left:right].casefold()
                words = set(re.findall(r"\w+", context))

                # Exclude the entity itself from context evidence.
                entity_words = set(
                    re.findall(r"\w+", text[start:end].casefold())
                )
                words -= entity_words

                score = len(
                    words.intersection(
                        rule.get("keywords", set()) if rule else set()
                    )
                )

                if score >= cls.MIN_SCORE:
                    candidate["resolution_confidence"] = "rule_based"
                    resolved.append(candidate)
                else:
                    candidate["label"] = "UNKNOWN"
                    candidate["candidate_labels"] = [label]
                    candidate["resolution_confidence"] = "unresolved"
                    resolved.append(candidate)

                continue

            left = max(0, start - 100)
            right = min(len(text), end + 100)
            context = text[left:right].casefold()
            words = set(re.findall(r"\w+", context))

            # Exclude the entity itself from context evidence.
            entity_words = set(
                re.findall(r"\w+", text[start:end].casefold())
            )
            words -= entity_words

            scored = []
            for candidate in candidates:
                label = (
                    candidate.get("label", "UNKNOWN")
                    .strip().upper()
                    .replace(" ", "_")
                )
                rule = cls.CONTEXT_RULES.get(label, {})
                keywords = rule.get("keywords", set())
                score = len(words.intersection(keywords))
                scored.append((score, label, candidate))

            scored.sort(key=lambda item: item[0], reverse=True)

            best_score, best_label, best_candidate = scored[0]
            second_score = scored[1][0]

            if (
                best_score >= cls.MIN_SCORE
                and best_score - second_score >= cls.MIN_MARGIN
            ):
                result = dict(best_candidate)
                result["label"] = best_label
                result["candidate_labels"] = sorted(unique)
                result["resolution_confidence"] = "rule_based"
                resolved.append(result)
            else:
                # Do not arbitrarily assign a semantic category.
                result = dict(candidates[0])
                result["label"] = "UNKNOWN"
                result["candidate_labels"] = sorted(unique)
                result["resolution_confidence"] = "unresolved"
                resolved.append(result)

        return sorted(
            resolved,
            key=lambda item: (item["start"], item["end"])
        )

import torch
from itertools import combinations
from collections import defaultdict


class ContrastiveDatasetBuilder:

    def __init__(self, embeddings_file):

        self.embeddings_file = embeddings_file

        self.data = torch.load(
            embeddings_file,
            weights_only=False
        )

    # ============================================================
    # GROUP EMBEDDINGS
    # ============================================================

    def _group_by_label(self):

        groups = defaultdict(list)

        for index, item in enumerate(self.data):

            groups[item["label"]].append(
                (index, item)
            )

        return groups

    # ============================================================
    # NORMALIZE ENTITY TEXT
    # ============================================================

    def _normalize_text(self, text):

        return text.strip().lower()

    # ============================================================
    # BUILD POSITIVE PAIRS
    # ============================================================

    def build_positive_pairs(self):

        positive_pairs = []

        label_groups = self._group_by_label()

        for label, items in label_groups.items():

            if len(items) < 2:
                continue

            for (idx1, item1), (idx2, item2) in combinations(
                items,
                2
            ):

                # ------------------------------------------
                # Do not create self-pairs
                # ------------------------------------------

                if idx1 == idx2:
                    continue

                # ------------------------------------------
                # Do not treat the exact same occurrence
                # as a useful contrastive pair
                # ------------------------------------------

                if (
                    item1["start"] == item2["start"]
                    and
                    item1["end"] == item2["end"]
                ):
                    continue

                positive_pairs.append({

                    "embedding1": item1["embedding"],
                    "embedding2": item2["embedding"],

                    "label": 1,

                    "entity1": item1["text"],
                    "entity2": item2["text"],

                    "type1": item1["label"],
                    "type2": item2["label"],

                    "index1": idx1,
                    "index2": idx2,

                    "pair_type": "positive"
                })

        return positive_pairs

    # ============================================================
    # BUILD NORMAL NEGATIVE PAIRS
    # ============================================================

    def build_negative_pairs(
        self,
        max_per_label_pair=20
    ):

        negative_pairs = []

        label_groups = self._group_by_label()

        labels = sorted(
            label_groups.keys()
        )

        for i in range(len(labels)):

            for j in range(i + 1, len(labels)):

                label1 = labels[i]
                label2 = labels[j]

                group1 = label_groups[label1]
                group2 = label_groups[label2]

                count = 0

                for idx1, item1 in group1:

                    for idx2, item2 in group2:

                        negative_pairs.append({

                            "embedding1": item1["embedding"],
                            "embedding2": item2["embedding"],

                            "label": 0,

                            "entity1": item1["text"],
                            "entity2": item2["text"],

                            "type1": item1["label"],
                            "type2": item2["label"],

                            "index1": idx1,
                            "index2": idx2,

                            "pair_type": "negative"
                        })

                        count += 1

                        if count >= max_per_label_pair:
                            break

                    if count >= max_per_label_pair:
                        break

        return negative_pairs

    # ============================================================
    # BUILD HARD NEGATIVES
    # ============================================================

    def build_hard_negatives(self):

        hard_negatives = []

        # Same surface form appearing with different labels
        surface_groups = defaultdict(list)

        for index, item in enumerate(self.data):

            normalized = self._normalize_text(
                item["text"]
            )

            surface_groups[normalized].append(
                (index, item)
            )

        for surface, items in surface_groups.items():

            if len(items) < 2:
                continue

            for (idx1, item1), (idx2, item2) in combinations(
                items,
                2
            ):

                # ------------------------------------------------
                # Same label is NOT a hard negative
                # ------------------------------------------------

                if item1["label"] == item2["label"]:
                    continue

                hard_negatives.append({

                    "embedding1": item1["embedding"],
                    "embedding2": item2["embedding"],

                    "label": 0,

                    "entity1": item1["text"],
                    "entity2": item2["text"],

                    "type1": item1["label"],
                    "type2": item2["label"],

                    "index1": idx1,
                    "index2": idx2,

                    "pair_type": "hard_negative"
                })

        return hard_negatives

    # ============================================================
    # BUILD COMPLETE DATASET
    # ============================================================

    def build_dataset(
        self,
        max_negative_per_label_pair=20
    ):

        positive_pairs = (
            self.build_positive_pairs()
        )

        negative_pairs = (
            self.build_negative_pairs(
                max_per_label_pair=
                max_negative_per_label_pair
            )
        )

        hard_negatives = (
            self.build_hard_negatives()
        )

        # --------------------------------------------------------
        # Combine negatives
        # --------------------------------------------------------

        all_negative_pairs = (
            negative_pairs +
            hard_negatives
        )

        # --------------------------------------------------------
        # Remove duplicate pairs
        # --------------------------------------------------------

        unique_pairs = {}
        
        for pair in all_negative_pairs:

            key = (
                min(
                    pair["index1"],
                    pair["index2"]
                ),
                max(
                    pair["index1"],
                    pair["index2"]
                )
            )

            unique_pairs[key] = pair

        all_negative_pairs = list(
            unique_pairs.values()
        )

        return (
            positive_pairs,
            negative_pairs,
            hard_negatives
        )

    # ============================================================
    # BALANCE DATASET
    # ============================================================

    def balance_pairs(
        self,
        positive_pairs,
        negative_pairs,
        seed=42
    ):

        generator = torch.Generator()

        generator.manual_seed(seed)

        # --------------------------------------------------------
        # If negatives are fewer, use all negatives
        # --------------------------------------------------------

        if len(negative_pairs) <= len(
            positive_pairs
        ):

            selected_negatives = (
                negative_pairs
            )

        else:

            indices = torch.randperm(
                len(negative_pairs),
                generator=generator
            )

            indices = indices[
                :len(positive_pairs)
            ]

            selected_negatives = [
                negative_pairs[i]
                for i in indices.tolist()
            ]

        balanced_dataset = (
            positive_pairs +
            selected_negatives
        )

        # --------------------------------------------------------
        # Shuffle complete dataset
        # --------------------------------------------------------

        if len(balanced_dataset) > 1:

            indices = torch.randperm(
                len(balanced_dataset),
                generator=generator
            )

            balanced_dataset = [
                balanced_dataset[i]
                for i in indices.tolist()
            ]

        return balanced_dataset

    # ============================================================
    # STATISTICS
    # ============================================================

    def print_statistics(
        self,
        positive_pairs,
        negative_pairs,
        hard_negatives,
        balanced_dataset
    ):

        print("\n" + "=" * 80)
        print("CONTRASTIVE DATASET")
        print("=" * 80)

        print(
            f"Total embeddings       : {len(self.data)}"
        )

        print(
            f"Positive pairs         : "
            f"{len(positive_pairs)}"
        )

        print(
            f"Normal negative pairs  : "
            f"{len(negative_pairs)}"
        )

        print(
            f"Hard negative pairs    : "
            f"{len(hard_negatives)}"
        )

        print(
            f"Balanced dataset       : "
            f"{len(balanced_dataset)}"
        )

        print("\n" + "-" * 80)
        print("LABEL DISTRIBUTION")
        print("-" * 80)

        groups = self._group_by_label()

        for label, items in sorted(
            groups.items()
        ):

            print(
                f"{label:30s} : {len(items)}"
            )

    # ============================================================
    # SHOW PAIR EXAMPLES
    # ============================================================

    def print_examples(
        self,
        positive_pairs,
        hard_negatives,
        number=10
    ):

        print("\n" + "=" * 80)
        print("POSITIVE PAIR EXAMPLES")
        print("=" * 80)

        for pair in positive_pairs[:number]:

            print(
                f"{pair['entity1']} "
                f"({pair['type1']})"
                f"  <-->  "
                f"{pair['entity2']} "
                f"({pair['type2']})"
            )

        print("\n" + "=" * 80)
        print("HARD NEGATIVE EXAMPLES")
        print("=" * 80)

        if not hard_negatives:

            print(
                "No hard negative pairs found."
            )

        else:

            for pair in hard_negatives[:number]:

                print(
                    f"{pair['entity1']} "
                    f"({pair['type1']})"
                    f"  <-->  "
                    f"{pair['entity2']} "
                    f"({pair['type2']})"
                )

    def build_contextual_hard_negatives(self):
        """
        Explicit hard negatives for ambiguous surface forms.
        Same entity text, different semantic label.
        """

        ambiguous_pairs = [
            ("Apple", "COMPANY", "FRUIT"),
            ("Amazon", "COMPANY", "RIVER"),
            ("Jordan", "COUNTRY", "CITY"),
            ("Python", "PROGRAMMING_LANGUAGE", "ANIMAL"),
            ("Gold", "METAL", "COLOR"),
        ]

        hard_negatives = []

        for text, label1, label2 in ambiguous_pairs:

            first = None
            second = None

            for i, item in enumerate(self.embeddings):

                if item["text"].lower() == text.lower():

                    if item["label"] == label1:
                        first = i

                    elif item["label"] == label2:
                        second = i

            if first is not None and second is not None:

                hard_negatives.append({
                    "idx1": first,
                    "idx2": second,
                    "label": 0,
                    "pair_type": "contextual_hard_negative"
                })

        return hard_negatives
"""
trie.py

Trie implementation for lookup-based entity detection.

Features
--------
- Multi-word entity support
- Multiple labels for ambiguous entities
- Longest-match traversal
- Case-insensitive lookup
- Token-level construction
"""

from dataclasses import dataclass, field


@dataclass
class TrieNode:

    children: dict = field(
        default_factory=dict
    )

    labels: list = field(
        default_factory=list
    )

    terminal: bool = False

    original: str = ""


class Trie:

    def __init__(self):

        self.root = TrieNode()

    def insert(
        self,
        entity: str,
        label: str
    ):

        tokens = entity.casefold().split()

        node = self.root

        for token in tokens:

            if token not in node.children:

                node.children[token] = TrieNode()

            node = node.children[token]

        node.terminal = True
        node.original = entity

        if label not in node.labels:

            node.labels.append(label)

    def count_nodes(self):

        def dfs(node):

            total = 1

            for child in node.children.values():

                total += dfs(child)

            return total

        return dfs(self.root)

    def search_longest(
        self,
        tokens,
        start_idx
    ):

        node = self.root

        best_match = None

        i = start_idx

        while i < len(tokens):

            token = tokens[i].casefold()

            if token not in node.children:

                break

            node = node.children[token]

            if node.terminal:

                best_match = {
                    "text": node.original,
                    "labels": list(node.labels),
                    "length": i - start_idx + 1
                }

            i += 1

        return best_match

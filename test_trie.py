from src.trie import Trie

trie = Trie()

trie.insert(
    "New York Stock Exchange",
    "ORGANIZATION"
)

trie.insert(
    "New York",
    "CITY"
)

trie.insert(
    "Bangalore",
    "CITY"
)

trie.insert(
    "cricket",
    "SPORT"
)

trie.insert(
    "cricket",
    "INSECT"
)

print("Trie nodes :", trie.count_nodes())
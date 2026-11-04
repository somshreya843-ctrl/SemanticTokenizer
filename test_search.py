from src.lookup_detector import LookupDetector

detector = LookupDetector()

tokens = "I live in Bangalore India".split()

print(detector.trie.search_longest(tokens, 3))

print(detector.trie.search_longest(tokens, 4))
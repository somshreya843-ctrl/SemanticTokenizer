from src.regex_detector import RegexDetector
from src.lookup_detector import LookupDetector
from src.gliner_detector import GLiNERDetector
from src.entity_merger import EntityMerger
from src.dictionary_expander import DictionaryExpander

with open("data/sample.txt") as f:
    text = f.read()

regex = RegexDetector()
lookup = LookupDetector()
gliner = GLiNERDetector()

regex_entities = regex.detect(text)
lookup_entities = lookup.detect(text)
gliner_entities = gliner.detect(text)

merger = EntityMerger()

merged = merger.merge(
    regex_entities,
    lookup_entities,
    gliner_entities
)

expander = DictionaryExpander()

suggestions = expander.suggest(
    merged,
    lookup_entities
)

print("\nSuggested Dictionary Entries\n")

for s in suggestions:
    print(s)
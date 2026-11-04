from src.regex_detector import RegexDetector
from src.lookup_detector import LookupDetector
from src.gliner_detector import GLiNERDetector
from src.entity_merger import EntityMerger
from src.placeholder_mapper import PlaceholderMapper

# Read sample text
with open("data/sample.txt", "r") as f:
    text = f.read()

print("=" * 50)
print("ORIGINAL TEXT")
print("=" * 50)
print(text)

# Run detectors
regex_detector = RegexDetector()
lookup_detector = LookupDetector()
gliner_detector = GLiNERDetector()

regex_entities = regex_detector.detect(text)
lookup_entities = lookup_detector.detect(text)
gliner_entities = gliner_detector.detect(text)

# Merge all entities
merger = EntityMerger()
entities = merger.merge(
    regex_entities,
    lookup_entities,
    gliner_entities
)

# Replace with placeholders
mapper = PlaceholderMapper()
semantic_text = mapper.replace(text, entities)

print("\n" + "=" * 50)
print("SEMANTIC TEXT")
print("=" * 50)
print(semantic_text)

print("\n" + "=" * 50)
print("DETECTED ENTITIES")
print("=" * 50)

for entity in entities:
    print(entity)
from src.regex_detector import RegexDetector
from src.lookup_detector import LookupDetector
from src.gliner_detector import GLiNERDetector
from src.entity_merger import EntityMerger

# Read sample text
with open("data/sample.txt", "r") as f:
    text = f.read()

# Create detectors
regex_detector = RegexDetector()
lookup_detector = LookupDetector()
gliner_detector = GLiNERDetector()

# Detect entities
regex_entities = regex_detector.detect(text)
lookup_entities = lookup_detector.detect(text)
gliner_entities = gliner_detector.detect(text)

# Merge
merger = EntityMerger()

all_entities = merger.merge(
    regex_entities,
    lookup_entities,
    gliner_entities
)

print("\nMerged Entities\n")

for entity in all_entities:
    print(entity)
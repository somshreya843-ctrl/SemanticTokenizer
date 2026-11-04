from src.regex_detector import RegexDetector
from src.lookup_detector import LookupDetector
from src.gliner_detector import GLiNERDetector
from src.entity_merger import EntityMerger
from src.document_mapper import DocumentMapper

# Read sample text
with open("data/sample.txt", "r") as f:
    text = f.read()

# Run detectors
regex = RegexDetector()
lookup = LookupDetector()
gliner = GLiNERDetector()

regex_entities = regex.detect(text)
lookup_entities = lookup.detect(text)
gliner_entities = gliner.detect(text)

# Merge entities
merger = EntityMerger()

merged_entities = merger.merge(
    regex_entities,
    lookup_entities,
    gliner_entities
)

# Assign document-level placeholders
mapper = DocumentMapper()

mapped_entities = mapper.assign(merged_entities)

print("\nMapped Entities\n")

for entity in mapped_entities:
    print(entity)
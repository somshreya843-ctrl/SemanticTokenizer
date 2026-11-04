
from src.regex_detector import RegexDetector
from src.lookup_detector import LookupDetector
from src.gliner_detector import GLiNERDetector
from src.entity_merger import EntityMerger
from src.document_mapper import DocumentMapper
from src.placeholder_mapper import PlaceholderMapper

# --------------------------------------------------
# 1. Load input
# --------------------------------------------------
with open("data/sample.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("=" * 60)
print("ORIGINAL TEXT")
print("=" * 60)
print(text)

# --------------------------------------------------
# 2. Detect entities
# --------------------------------------------------
regex = RegexDetector()
lookup = LookupDetector()
gliner = GLiNERDetector()

regex_entities = regex.detect(text)
lookup_entities = lookup.detect(text)
gliner_entities = gliner.detect(text)

# --------------------------------------------------
# 3. Merge detections and assign placeholders
# --------------------------------------------------
merger = EntityMerger()

merged_entities = merger.merge(
    regex_entities,
    lookup_entities,
    gliner_entities,
)

doc_mapper = DocumentMapper()
mapped_entities = doc_mapper.assign(merged_entities)

# --------------------------------------------------
# 4. Generate semantic output
# --------------------------------------------------
placeholder_mapper = PlaceholderMapper()
semantic_text = placeholder_mapper.replace(text, mapped_entities)

print("\n" + "=" * 60)
print("SEMANTIC OUTPUT")
print("=" * 60)
print(semantic_text)

# --------------------------------------------------
# 5. Print detected entities
# --------------------------------------------------
print("\n" + "=" * 60)
print("DETECTED ENTITIES")
print("=" * 60)

for entity in sorted(
    mapped_entities,
    key=lambda e: (e.get("start", 0), e.get("end", 0)),
):
    print({
        "text": entity.get("text"),
        "label": entity.get("label"),
        "start": entity.get("start"),
        "end": entity.get("end"),
        "score": entity.get("score"),
        "source": entity.get("source"),
        "placeholder": entity.get("placeholder"),
    })

# --------------------------------------------------
# 6. Print regex detection results separately
# --------------------------------------------------
print("\n" + "=" * 60)
print("REGEX DETECTION RESULTS")
print("=" * 60)

for entity in sorted(
    regex_entities,
    key=lambda e: (e.get("start", 0), e.get("end", 0)),
):
    print(entity)

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

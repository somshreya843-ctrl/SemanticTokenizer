from src.gliner_detector import GLiNERDetector

# Read sample text
with open("data/sample.txt", "r") as f:
    text = f.read()

# Load model
detector = GLiNERDetector()

# Detect entities
entities = detector.detect(text)

print("\nGLiNER Detected Entities:\n")

for entity in entities:
    print(entity)
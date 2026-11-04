
from src.corpus_processor import CorpusProcessor

samples = [
    "Apple released a new product.",
    "She ate a fresh apple.",
    "Python is a popular programming language.",
    "I like this book.",
]

processor = CorpusProcessor()

for i, text in enumerate(samples, start=1):
    print(f"\n\nTEST {i}: {text}")
    processor.process_document(
        text=text,
        document_name=f"terminal_test_{i}",
        terminal_only=True,
    )

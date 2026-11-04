from src.corpus_generator import CorpusGenerator

generator = CorpusGenerator()

generator.generate(
    max_documents=10,
    output_folder="output"
)
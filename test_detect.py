from src.lookup_detector import LookupDetector

detector = LookupDetector()

text = "John works at New York Stock Exchange in Bangalore India"

entities = detector.detect(text)

for e in entities:
    print(e)
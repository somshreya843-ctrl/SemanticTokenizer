from src.lookup_detector import LookupDetector

detector = LookupDetector()

text = """
John lives in Bangalore, India.
He works at Google.
"""

segments = detector.segment_text(text)

for s in segments:
    print(s)
from src.lookup_detector import LookupDetector

detector = LookupDetector()

text = """
My email is abc@gmail.com.
I live in Bangalore.
"""

result = detector.parse(text)

for r in result:

    print()

    print("ID       :", r["id"])
    print("Original :", r["original"])

    print("Parsed   :", r["parsed"])

    print("Entities :", r["entities"])
    print("Metadata :", r["metadata"])
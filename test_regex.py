from src.regex_detector import RegexDetector

detector = RegexDetector()

text = """
My email is abc@gmail.com.
Visit https://openai.com.
Today is 2026-08-01.
My IP is 192.168.1.1.
Call me at +91-9876543210.
"""

entities = detector.detect(text)

print("\nDetected entities:\n")

for e in entities:
    print(e)
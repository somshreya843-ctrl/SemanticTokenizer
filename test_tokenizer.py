import sentencepiece as spm

sp = spm.SentencePieceProcessor()
sp.load("output/semantic_tokenizer.model")

text = """
<PERSON> works at <ORG> in <LOCATION>.
"""

print("Original Text:")
print(text)

print("\nTokens:")
print(sp.encode(text, out_type=str))

print("\nToken IDs:")
print(sp.encode(text, out_type=int))
import sentencepiece as spm

sp = spm.SentencePieceProcessor()
sp.load("output/semantic_tokenizer.model")

original = """
John Smith works at Google in Bengaluru.
"""

semantic = """
<PERSON> works at <ORG> in <LOCATION>.
"""

original_tokens = sp.encode(original, out_type=str)
semantic_tokens = sp.encode(semantic, out_type=str)

print("=" * 60)
print("ORIGINAL")
print("=" * 60)
print(original)

print("\nTokens:")
print(original_tokens)

print("\nNumber of Tokens:", len(original_tokens))

print("\n" + "=" * 60)
print("SEMANTIC")
print("=" * 60)
print(semantic)

print("\nTokens:")
print(semantic_tokens)

print("\nNumber of Tokens:", len(semantic_tokens))

reduction = (
    (len(original_tokens) - len(semantic_tokens))
    / len(original_tokens)
) * 100

print("\n" + "=" * 60)
print(f"Token Reduction: {reduction:.2f}%")
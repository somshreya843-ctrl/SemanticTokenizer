from src.corpus_processor import CorpusProcessor

import torch
from pathlib import Path


processor = CorpusProcessor()

# Store embeddings from ALL test cases
all_embeddings = []


# ============================================================
# INDIVIDUAL ENTITY VERIFICATION
# ============================================================

entities_to_verify = [
    "Tesla",
    "Elon Musk",
    "Stanford University",
    "Google",
    "Microsoft",
    "Apple",
    "Amazon",
    "India",
    "Bangalore",
    "Hyderabad",

    # Add the remaining entities here
]


test_cases = [

    # =====================================================
    # Geography
    # =====================================================

    {"input": "I live in Bangalore."},
    {"input": "India is a country."},
    {"input": "Mount Everest is the highest mountain."},
    {"input": "The Ganga is a famous river."},
    {"input": "I visited Victoria Memorial."},
    {"input": "I studied at Stanford University."},
    {"input": "The flight landed at Indira Gandhi International Airport."},
    {"input": "The Amazon rainforest is huge."},
    {"input": "The Nile flows through Egypt."},
    {"input": "Golden Gate Bridge is in California."},

    # =====================================================
    # Entertainment
    # =====================================================

    {"input": "Shah Rukh Khan acted in Pathaan."},
    {"input": "Christopher Nolan directed Interstellar."},
    {"input": "Hans Zimmer composed the soundtrack."},
    {"input": "Avatar is a famous movie."},
    {"input": "Tom Cruise starred in Top Gun."},
    {"input": "Leonardo DiCaprio acted in Titanic."},
    {"input": "Steven Spielberg directed Jurassic Park."},

    # =====================================================
    # Business
    # =====================================================

    {"input": "Google released Gemini."},
    {"input": "Microsoft owns GitHub."},
    {"input": "Apple launched the iPhone."},
    {"input": "Amazon hired many engineers."},
    {"input": "Tesla manufactures electric cars."},

    # =====================================================
    # Technology
    # =====================================================

    {"input": "Python is a programming language."},
    {"input": "Java is object oriented."},
    {"input": "Rust is memory safe."},
    {"input": "C++ is very fast."},
    {"input": "JavaScript runs inside browsers."},

    # =====================================================
    # Medicine
    # =====================================================

    {"input": "I have diabetes."},
    {"input": "Take Paracetamol."},
    {"input": "Fever is a symptom."},
    {"input": "COVID-19 vaccine is available."},
    {"input": "The doctor performed angioplasty."},
    {"input": "MRI is a diagnostic test."},
    {"input": "She received insulin."},
    {"input": "Tuberculosis is a disease."},

    # =====================================================
    # Science
    # =====================================================

    {"input": "Hydrogen is an element."},
    {"input": "Gold is a metal."},
    {"input": "Oxygen is a gas."},
    {"input": "Quartz is a mineral."},
    {"input": "Sulfuric acid is dangerous."},
    {"input": "Sodium chloride is a salt."},
    {"input": "Polyethylene is a polymer."},

    # =====================================================
    # Agriculture
    # =====================================================

    {"input": "Rice is a crop."},
    {"input": "Urea is a fertilizer."},
    {"input": "Glyphosate is a herbicide."},
    {"input": "Nitrogen is a nutrient."},
    {"input": "The farmer bought a tractor."},
    {"input": "DDT is a pesticide."},

    # =====================================================
    # Regex
    # =====================================================

    {"input": "My email is abc@gmail.com."},
    {"input": "Contact me at xyz@yahoo.co.in."},
    {"input": "Visit https://openai.com."},
    {"input": "Today's date is 2026-08-01."},
    {"input": "Meeting is on 01/08/2026."},
    {"input": "Call me at +91-9876543210."},
    {"input": "My IP is 192.168.1.1."},
    {"input": "MAC address is 00:1A:2B:3C:4D:5E."},
    {"input": "PAN number is ABCDE1234F."},
    {"input": "Aadhaar is 1234 5678 9012."},

    # =====================================================
    # Mixed Entities
    # =====================================================

    {"input": "Google hired Rahul in Bangalore."},
    {"input": "Christopher Nolan visited India."},
    {"input": "Python was developed before Rust."},
    {"input": "Paracetamol was prescribed after MRI."},
    {"input": "Amazon opened a new office in Hyderabad."},
    {"input": "Tesla CEO Elon Musk visited Stanford University."},

    # =====================================================
    # Multiple entities
    # =====================================================

    {"input": "Google and Microsoft opened offices in Bangalore and Hyderabad."},
    {"input": "Shah Rukh Khan and Salman Khan acted together."},
    {"input": "India and China are neighbouring countries."},
    {"input": "Gold and Silver are precious metals."},
    {"input": "Rice and Wheat are important crops."},

    # =====================================================
    # Repeated entities
    # =====================================================

    {"input": "Google Google Google announced Google AI."},
    {"input": "Python Python Python is popular."},
    {"input": "India India India."},

    # =====================================================
    # Negative tests
    # =====================================================

    {"input": "The cat is sleeping."},
    {"input": "I like ice cream."},
    {"input": "Today is sunny."},
    {"input": "She enjoys dancing."},
    {"input": "He reads books every day."},
    {"input": "The quick brown fox jumps over the lazy dog."},

    # =====================================================
    # Ambiguous Entity Tests
    # =====================================================

    {"input": "Apple is a company."},
    {"input": "I ate an apple."},

    {"input": "Amazon is a company."},
    {"input": "The Amazon is a river."},

    {"input": "Jordan is a country."},
    {"input": "Jordan played basketball."},

    {"input": "Python is a programming language."},
    {"input": "A python is a snake."},

    {"input": "Gold is a metal."},
    {"input": "The gold looks shiny."},

]


# ============================================================
# INDIVIDUAL ENTITY VERIFICATION
# ============================================================

print("\n" + "=" * 100)
print("INDIVIDUAL ENTITY VERIFICATION")
print("=" * 100)


for i, entity in enumerate(
    entities_to_verify,
    start=1
):

    test_sentence = f"{entity} is being tested."

    (
        output,
        detected_entities,
        embedded_entities
    ) = processor.process_document(
        test_sentence
    )

    # --------------------------------------------------------
    # Collect embeddings
    # --------------------------------------------------------

    all_embeddings.extend(
        embedded_entities
    )

    print("\n" + "-" * 100)

    print(
        f"ENTITY {i}/{len(entities_to_verify)}"
    )

    print(
        f"INPUT  : {test_sentence}"
    )

    print(
        f"OUTPUT : {output}"
    )

    print("\nENTITIES:")

    if detected_entities:

        for detected in detected_entities:
            print(detected)

    else:

        print("No entities detected.")


# ============================================================
# MAIN TEST CASES
# ============================================================

passed = 0
failed = 0


for i, case in enumerate(
    test_cases,
    start=1
):

    (
        output,
        entities,
        embedded_entities
    ) = processor.process_document(
        case["input"]
    )

    # --------------------------------------------------------
    # Collect embeddings
    # --------------------------------------------------------

    all_embeddings.extend(
        embedded_entities
    )

    print("\n" + "=" * 100)

    print(
        f"TEST {i}"
    )

    print(
        f"INPUT  : {case['input']}"
    )

    print(
        f"OUTPUT : {output}"
    )

    print("\nENTITIES:")

    if entities:

        for entity in entities:
            print(entity)

    else:

        print("No entities detected.")

    # --------------------------------------------------------
    # Automatic check
    # --------------------------------------------------------

    if "expected" in case:

        print(
            f"\nEXPECTED : {case['expected']}"
        )

        if output == case["expected"]:

            print(
                "STATUS   : ✅ PASSED"
            )

            passed += 1

        else:

            print(
                "STATUS   : ❌ FAILED"
            )

            failed += 1


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)

print(
    f"Total Tests : {len(test_cases)}"
)


if passed + failed > 0:

    print(
        f"Passed      : {passed}"
    )

    print(
        f"Failed      : {failed}"
    )

    if failed == 0:

        print(
            "\n🎉 ALL TESTS PASSED"
        )

    else:

        print(
            "\n⚠️ SOME TESTS FAILED"
        )

else:

    print(
        "Manual verification mode (no expected outputs provided)."
    )


# ============================================================
# SAVE ALL EMBEDDINGS
# ============================================================

print("\n" + "=" * 100)
print("EMBEDDING STORAGE")
print("=" * 100)


# Create directory
embedding_dir = Path(
    "data/embeddings"
)

embedding_dir.mkdir(
    parents=True,
    exist_ok=True
)


# Save ALL embeddings together
embedding_file = (
    embedding_dir /
    "test_embeddings.pt"
)


torch.save(
    all_embeddings,
    embedding_file
)


print(
    f"Total entity embeddings saved : {len(all_embeddings)}"
)

print(
    f"Embedding dimension            : 768"
)

print(
    f"Saved to                       : {embedding_file}"
)

print(
    "\nEmbeddings saved successfully."
)
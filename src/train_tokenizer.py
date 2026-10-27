import sentencepiece as spm


def train():

    spm.SentencePieceTrainer.train(

        input="output/semantic_corpus.txt",

        model_prefix="output/semantic_tokenizer",

        vocab_size=1000,

        model_type="bpe",

        character_coverage=1.0,

        user_defined_symbols=[
            "<PERSON>",
            "<ORG>",
            "<LOCATION>",
            "<DATE>",
            "<EMAIL>",
            "<PHONE>",
            "<URL>",
            "<IP>",
            "<PINCODE>"
        ]
    )

    print("\nTokenizer Training Finished")


if __name__ == "__main__":
    train()
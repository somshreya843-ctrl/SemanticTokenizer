
import torch
from transformers import AutoTokenizer, AutoModel


class ContextEmbedder:
    def __init__(self, model_name="bert-base-uncased"):
        self.device = torch.device(
            "mps" if torch.backends.mps.is_available()
            else "cuda" if torch.cuda.is_available()
            else "cpu"
        )

        print(f"Using device: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def encode(self, context, entity, category=None, start=None, end=None):
        context = str(context)
        entity = str(entity)

        # Mark the exact entity span whenever possible.
        valid_span = (
            isinstance(start, int)
            and isinstance(end, int)
            and 0 <= start < end <= len(context)
            and context[start:end].casefold() == entity.casefold()
        )

        if valid_span:
            marked_context = (
                context[:start]
                + " [ENTITY] "
                + context[start:end]
                + " [/ENTITY] "
                + context[end:]
            )
        else:
            # Use offsets only when they match; otherwise require
            # one unambiguous occurrence in the context.
            positions = []
            search_from = 0

            while entity and search_from < len(context):
                pos = context.casefold().find(
                    entity.casefold(), search_from
                )
                if pos == -1:
                    break

                before_ok = (
                    pos == 0 or not (
                        context[pos - 1].isalnum()
                        or context[pos - 1] == "_"
                    )
                )
                after = pos + len(entity)
                after_ok = (
                    after == len(context) or not (
                        context[after].isalnum()
                        or context[after] == "_"
                    )
                )

                if before_ok and after_ok:
                    positions.append(pos)

                search_from = pos + max(1, len(entity))

            if len(positions) == 1:
                pos = positions[0]
                end_pos = pos + len(entity)
                marked_context = (
                    context[:pos]
                    + " [ENTITY] "
                    + context[pos:end_pos]
                    + " [/ENTITY] "
                    + context[end_pos:]
                )
            else:
                # Do not guess which occurrence is the target.
                marked_context = (
                    f"Target entity: {entity}. Context: {context}"
                )

        inputs = self.tokenizer(
            marked_context,
            return_tensors="pt",
            truncation=True,
            max_length=256
        )
        inputs = {key: value.to(self.device)
                  for key, value in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        # Attention-mask-aware mean pooling.
        mask = inputs["attention_mask"].unsqueeze(-1).to(
            outputs.last_hidden_state.dtype
        )
        embedding = (
            (outputs.last_hidden_state * mask).sum(dim=1)
            / mask.sum(dim=1).clamp(min=1e-9)
        )

        return embedding[0].cpu()

    def encode_entities(self, text, entities):
        results = []

        for entity in entities:
            entity_text = entity.get("text", entity.get("entity", ""))
            category = entity.get(
                "category", entity.get("label", "unknown")
            )

            embedding = self.encode(
                context=text,
                entity=entity_text,
                category=category,
                start=entity.get("start"),
                end=entity.get("end")
            )

            results.append({
                "text": entity_text,
                "label": entity.get("label"),
                "category": category,
                "start": entity.get("start"),
                "end": entity.get("end"),
                "source": entity.get("source"),
                "placeholder": entity.get("placeholder"),
                "embedding": embedding
            })

        return results

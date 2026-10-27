from dataclasses import dataclass


@dataclass
class Entity:

    text: str

    label: str

    start: int
    end: int

    source: str

    confidence: float

    metadata: dict | None = None

    placeholder: str | None = None
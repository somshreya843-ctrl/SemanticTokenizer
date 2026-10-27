from dataclasses import dataclass


@dataclass
class EntitySource:
    name: str
    category: str
    provider: str
    identifier: str

    column: str

    country_code: str | None = None
    feature_class: str | None = None
    feature_code: str | None = None

    encoding: str = "utf-8"
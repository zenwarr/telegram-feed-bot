from dataclasses import dataclass


@dataclass()
class TextWithEntities:
    text: str
    entities: list

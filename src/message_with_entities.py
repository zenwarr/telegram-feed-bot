from dataclasses import dataclass


@dataclass()
class MessageWithEntities:
    text: str
    entities: list

from dataclasses import dataclass, field


@dataclass
class Product:
    name: str
    url: str
    flavours: field(default_factory=list)

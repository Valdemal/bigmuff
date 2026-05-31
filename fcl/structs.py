from typing import Callable, Iterable

from attr import dataclass

from builder import Builder
from fcl.enums import FCLTokens, FCLRules


# Структура лексемы
@dataclass
class FCLElement:
    id: FCLTokens
    value: str
    str_pos: int
    chr_pos: int


@dataclass
class FCLMatrixSymbol:
    pop: bool
    next: bool
    action: Callable[[FCLElement, Builder], None] = None
    to_stack: Iterable[FCLTokens | FCLRules] = ()

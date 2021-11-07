import dataclasses
from typing import NamedTuple


@dataclasses.dataclass
class AntState:
    x: int
    y: int
    direction: int
    state: int


class Rule(NamedTuple):
    state: int
    colour: int
    new_state: int
    new_colour: int
    turn: int

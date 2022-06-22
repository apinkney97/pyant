from typing import NamedTuple, NewType

AntState = NewType("AntState", int)
Colour = NewType("Colour", int)


class Rule(NamedTuple):
    state: AntState
    colour: Colour
    new_state: AntState
    new_colour: Colour
    turn: int

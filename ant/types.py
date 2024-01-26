from enum import IntEnum
from typing import NamedTuple, NewType

AntColour = NewType("AntColour", int)
CellColour = NewType("CellColour", int)


class Rule(NamedTuple):
    ant_colour: AntColour
    cell_colour: CellColour
    new_ant_colour: AntColour
    new_cell_colour: CellColour
    turn: int


class CardinalDirection(IntEnum):
    NORTH = 1
    NORTH_EAST = 2
    EAST = 3
    SOUTH_EAST = 4
    SOUTH = 5
    SOUTH_WEST = 6
    WEST = 7
    NORTH_WEST = 8

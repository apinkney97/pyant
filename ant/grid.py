from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable, NewType, Optional

Colour = NewType("Colour", int)


@dataclass(frozen=True)
class Vector:
    dx: int
    dy: int


@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    def __add__(self, vector: Vector):
        return Coord(self.x + vector.dx, self.y + vector.dy)

    def __radd__(self, vector: Vector):
        return self + vector


class CardinalDirection(IntEnum):
    NORTH = 1
    NORTH_EAST = 2
    EAST = 3
    SOUTH_EAST = 4
    SOUTH = 5
    SOUTH_WEST = 6
    WEST = 7
    NORTH_WEST = 8


class InvalidCoord(Exception):
    def __init__(self, coord: Coord):
        super().__init__(f"Invalid coordinate {coord}")


class InvalidDirection(Exception):
    def __init__(self, direction: CardinalDirection, coord: Optional[Coord] = None):
        extra_msg = "" if not coord else f" for coord {coord}"
        super().__init__(f"Bad direction {direction}{extra_msg}")


class Grid(ABC):
    """
    An unbounded grid, where each cell is coloured.

    All cells begin coloured in the default colour.
    """

    def __init__(self, default_colour: Colour = Colour(0)):
        self._default_colour = default_colour
        self._grid: dict[Coord, Colour] = {}

    def __getitem__(self, coord: Coord) -> Colour:
        self._check_coord(coord)
        return self._grid.get(coord, self._default_colour)

    def __setitem__(self, coord: Coord, value: Colour) -> None:
        self._check_coord(coord)
        if value == self._default_colour:
            self._grid.pop(coord)
        else:
            self._grid[coord] = value

    def __iter__(self) -> Iterable[tuple[Coord, Colour]]:
        for coord, value in self._grid.items():
            yield coord, value

    @property
    @abstractmethod
    def directions(self) -> dict[CardinalDirection, Vector]:
        pass

    def get_direction(
        self, old_direction: CardinalDirection, turn: int
    ) -> CardinalDirection:
        # 1 is forward, 2 is first step clockwise and so on
        turn = turn - 1
        directions = sorted(self.directions.keys())
        old_index = directions.index(old_direction)
        return directions[(old_index + turn) % len(self.directions)]

    def _check_coord(self, coord: Coord):
        if not self._validate_coord(coord):
            raise InvalidCoord(coord)

    def get_neighbour(self, coord: Coord, direction: CardinalDirection) -> Coord:
        self._check_coord(coord)
        if direction not in self.directions:
            raise InvalidDirection(direction)
        return coord + self.directions[direction]

    def _validate_coord(self, coord: Coord) -> bool:
        # All coords are valid in square and hex grids
        return True

    # @property
    # @abstractmethod
    # def bbox(self):
    #     pass


class SquareGrid(Grid):
    @property
    def directions(self) -> dict[CardinalDirection, Vector]:
        return {
            CardinalDirection.NORTH: Vector(0, 1),
            CardinalDirection.EAST: Vector(1, 0),
            CardinalDirection.SOUTH: Vector(0, -1),
            CardinalDirection.WEST: Vector(-1, 0),
        }


class HexGrid(Grid):
    # Handy: https://www.redblobgames.com/grids/hexagons/
    @property
    def directions(self) -> dict[CardinalDirection, Vector]:
        return {
            CardinalDirection.EAST: Vector(1, 0),
            CardinalDirection.WEST: Vector(-1, 0),
            CardinalDirection.NORTH_EAST: Vector(0, 1),
            CardinalDirection.SOUTH_WEST: Vector(0, -1),
            CardinalDirection.NORTH_WEST: Vector(-1, 1),
            CardinalDirection.SOUTH_EAST: Vector(1, -1),
        }


class TriangleGrid(Grid):
    # This uses the triangular coordinate scheme outlined here:
    # https://github.com/mhwombat/grid/wiki/Implementation%3A-Triangular-tiles

    _even_dirs = {
        CardinalDirection.NORTH_EAST,
        CardinalDirection.NORTH_WEST,
        CardinalDirection.SOUTH,
    }
    _odd_dirs = {
        CardinalDirection.NORTH,
        CardinalDirection.SOUTH_WEST,
        CardinalDirection.SOUTH_EAST,
    }

    @property
    def directions(self) -> dict[CardinalDirection, Vector]:
        return {
            CardinalDirection.NORTH: Vector(-1, 1),
            CardinalDirection.SOUTH: Vector(1, -1),
            CardinalDirection.SOUTH_EAST: Vector(1, -1),
            CardinalDirection.NORTH_WEST: Vector(-1, 1),
            CardinalDirection.SOUTH_WEST: Vector(-1, -1),
            CardinalDirection.NORTH_EAST: Vector(1, 1),
        }

    def get_direction(
        self, old_direction: CardinalDirection, turn: int
    ) -> CardinalDirection:
        if old_direction in self._even_dirs:
            old_dirs = self._even_dirs
            new_dirs = self._odd_dirs
        elif old_direction in self._odd_dirs:
            old_dirs = self._odd_dirs
            new_dirs = self._even_dirs
            turn = turn - 1
        else:
            raise InvalidDirection(old_direction)

        old_index = sorted(old_dirs).index(old_direction)
        # print(f"{old_index = }")
        # print(f"{sorted(new_dirs) = }")
        return sorted(new_dirs)[(old_index + turn) % 3]

    def _validate_coord(self, coord: Coord) -> bool:
        # Only (odd, odd) or (even, even) coords are valid
        return coord.x % 2 == coord.y % 2

    def get_neighbour(self, coord: Coord, direction: CardinalDirection) -> Coord:
        self._check_coord(coord)
        # The above check also happens later in the super() call, but it probably
        # makes sense to catch it earlier to avoid misleading errors about invalid
        # directions for invalid coordinates.

        if direction not in self.directions:
            raise InvalidDirection(direction)

        valid_dirs = self._even_dirs if coord.x % 2 == 0 else self._odd_dirs

        if direction not in valid_dirs:
            raise InvalidDirection(direction, coord)

        return super().get_neighbour(coord, direction)

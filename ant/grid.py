from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterable, Optional


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


class CardinalDirection(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()
    NORTH_EAST = auto()
    SOUTH_EAST = auto()
    SOUTH_WEST = auto()
    NORTH_WEST = auto()


class InvalidCoord(Exception):
    def __init__(self, coord: Coord):
        super().__init__(f"Invalid coordinate {coord}")


class InvalidDirection(Exception):
    def __init__(self, direction: CardinalDirection, coord: Optional[Coord] = None):
        extra_msg = "" if not coord else f" for coord {coord}"
        super().__init__(f"Bad direction {direction}{extra_msg}")


class Grid(ABC):
    def __init__(self, default_value: int = 0):
        self._default_value = default_value
        self._grid: dict[Coord, int] = {}

    def __getitem__(self, coord: Coord) -> int:
        self._check_coord(coord)
        return self._grid.get(coord, self._default_value)

    def __setitem__(self, coord: Coord, value: int) -> None:
        self._check_coord(coord)
        if value == self._default_value:
            self._grid.pop(coord)
        else:
            self._grid[coord] = value

    def __iter__(self) -> Iterable[tuple[Coord, int]]:
        for coord, value in self._grid.items():
            yield coord, value

    @property
    @abstractmethod
    def directions(self) -> dict[CardinalDirection, Vector]:
        pass

    def _check_coord(self, coord: Coord):
        if not self._validate_coord(coord):
            raise InvalidCoord(coord)

    def get_neighbour(self, coord: Coord, direction: CardinalDirection) -> Coord:
        self._check_coord(coord)
        if direction not in self.directions:
            raise InvalidDirection(direction)
        return coord + self.directions[direction]

    @abstractmethod
    def _validate_coord(self, coord: Coord) -> bool:
        pass

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

    def _validate_coord(self, coord: Coord) -> bool:
        # All coords are valid
        return True


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

    def _validate_coord(self, coord: Coord) -> bool:
        # All coords are valid
        return True


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

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable, NamedTuple, Optional

from ant.types import AntState, Colour, Rule


@dataclass(frozen=True)
class Vector:
    dx: int
    dy: int

    def __add__(self, other: Vector):
        if not isinstance(other, Vector):
            return NotImplemented

        return Vector(self.dx + other.dx, self.dy + other.dy)

    def __radd__(self, other: Vector):
        if not isinstance(other, Vector):
            return NotImplemented

        return self + other


@dataclass(frozen=True)
class GridCoord:
    x: int
    y: int

    def __add__(self, vector: Vector):
        if not isinstance(vector, Vector):
            return NotImplemented

        return GridCoord(self.x + vector.dx, self.y + vector.dy)

    def __radd__(self, vector: Vector):
        if not isinstance(vector, Vector):
            return NotImplemented

        return self + vector


class DisplayCoord(NamedTuple):
    x: float
    y: float


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
    def __init__(self, coord: GridCoord):
        super().__init__(f"Invalid coordinate {coord}")


class InvalidDirection(Exception):
    def __init__(self, direction: CardinalDirection, coord: Optional[GridCoord] = None):
        extra_msg = "" if not coord else f" for coord {coord}"
        super().__init__(f"Bad direction {direction!r}{extra_msg}")


class Grid(ABC):
    """
    An unbounded grid, where each cell is coloured.

    All cells begin coloured in the default colour.
    """

    _cell_vertices_cache: dict[GridCoord, tuple[DisplayCoord]]

    def __init__(self, default_colour: Colour = Colour(0), store_default: bool = False):
        self._default_colour = default_colour
        self._store_default = store_default
        self._grid: dict[GridCoord, Colour] = {}

        # Used for the "fast" bbox (which does not take into account true grid geometry)
        self._has_data = False
        self._min_x: int = 0
        self._min_y: int = 0
        self._max_x: int = 0
        self._max_y: int = 0

    def __init_subclass__(cls, **kwargs):
        cls._cell_vertices_cache = {}

    def __getitem__(self, coord: GridCoord) -> Colour:
        self._check_coord(coord)
        return self._grid.get(coord, self._default_colour)

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return self._min_x, self._min_y, self._max_x, self._max_y

    def __setitem__(self, coord: GridCoord, colour: Colour) -> None:
        self._check_coord(coord)

        # Update the bbox values
        if self._has_data:
            self._min_x = min(self._min_x, coord.x)
            self._max_x = max(self._max_x, coord.x)
            self._min_y = min(self._min_y, coord.y)
            self._max_y = max(self._max_y, coord.y)
        else:
            self._has_data = True
            self._min_x = self._max_x = coord.x
            self._min_y = self._max_y = coord.y

        if colour == self._default_colour and not self._store_default:
            self._grid.pop(coord)
        else:
            self._grid[coord] = colour

    def __iter__(self) -> Iterable[tuple[GridCoord, Colour]]:
        for coord, colour in self._grid.items():
            yield coord, colour

    @classmethod
    def get_cell_vertices(cls, coord: GridCoord) -> tuple[DisplayCoord, ...]:
        """Returns the 2d coordinates of the cell's vertices, to be used for rendering."""
        try:
            display_coord = cls._cell_vertices_cache[coord]
        except KeyError:
            display_coord = cls._get_cell_vertices(coord)
            cls._cell_vertices_cache[coord] = display_coord
        return display_coord

    @classmethod
    @abstractmethod
    def _get_cell_vertices(cls, coord: GridCoord) -> tuple[DisplayCoord, ...]:
        pass

    def get_display_bbox(self) -> tuple[int, int, int, int]:
        # This will probably be very inefficient when we have lots of coordinates...
        coords = list(self._grid.keys())

        if not coords:
            return 0, 0, 0, 0

        first = self.get_cell_vertices(coords[0])[0]
        max_x = min_x = first.x
        max_y = min_y = first.y

        for grid_coord in self._grid:
            for display_coord in self.get_cell_vertices(grid_coord):
                min_x = min(min_x, display_coord.x)
                min_y = min(min_y, display_coord.y)
                max_x = max(max_x, display_coord.x)
                max_y = max(max_y, display_coord.y)

        return min_x, min_y, max_x, max_y

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

    def _check_coord(self, coord: GridCoord):
        if not self._validate_coord(coord):
            raise InvalidCoord(coord)

    def get_neighbour(
        self, coord: GridCoord, direction: CardinalDirection
    ) -> GridCoord:
        self._check_coord(coord)
        if direction not in self.directions:
            raise InvalidDirection(direction)
        return coord + self.directions[direction]

    def _validate_coord(self, coord: GridCoord) -> bool:
        # All coords are valid in square and hex grids
        return True

    @classmethod
    @abstractmethod
    def lr_directions(cls) -> dict[str, int]:
        pass

    @classmethod
    def rules_from_lr_string(cls, lr_string: str) -> list[Rule]:
        # LR string rules are all in state 0, and have one colour per character.
        state = AntState(0)
        rules = []
        dirs = cls.lr_directions()
        for colour, turn_dir in enumerate(lr_string.upper()):
            if turn_dir not in dirs:
                raise ValueError(f"Bad LR string value for {cls.__name__}: {turn_dir}")

            rules.append(
                Rule(
                    state=state,
                    colour=Colour(colour),
                    new_state=state,
                    new_colour=Colour((colour + 1) % len(lr_string)),
                    turn=dirs[turn_dir],
                )
            )
        return rules


class SquareGrid(Grid):
    @property
    def directions(self) -> dict[CardinalDirection, Vector]:
        return {
            CardinalDirection.NORTH: Vector(0, 1),
            CardinalDirection.EAST: Vector(1, 0),
            CardinalDirection.SOUTH: Vector(0, -1),
            CardinalDirection.WEST: Vector(-1, 0),
        }

    @classmethod
    def _get_cell_vertices(cls, coord: GridCoord) -> tuple[DisplayCoord, ...]:
        left = coord.x
        right = coord.x + 1
        top = coord.y + 1
        bottom = coord.y
        return (
            DisplayCoord(left, top),
            DisplayCoord(right, top),
            DisplayCoord(right, bottom),
            DisplayCoord(left, bottom),
        )

    @classmethod
    def lr_directions(cls) -> dict[str, int]:
        return {
            "F": 1,
            "R": 2,
            "B": 3,
            "L": 4,
        }


class HexGrid(Grid):
    # Handy: https://www.redblobgames.com/grids/hexagons/
    # This is a "pointy-topped" grid, ie cells lie in horizontal rows.
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

    @classmethod
    def _get_cell_vertices(cls, coord: GridCoord) -> tuple[DisplayCoord, ...]:
        #  /`\
        # | C |
        #  \./

        # We define centre to centre horizontally to be 1 unit.
        # Therefore the "size" of the hexagons (centre to any vertex) is 1/sqrt(3)
        size = 3 ** -0.5

        centre_x = coord.x + (coord.y % 2) / 2
        left_x = centre_x - 0.5
        right_x = centre_x + 0.5

        centre_y = coord.y / (size * 2)
        top_y = centre_y + size
        upper_mid_y = centre_y + size / 2
        lower_mid_y = centre_y - size / 2
        bottom_y = centre_y - size

        return (
            DisplayCoord(centre_x, top_y),
            DisplayCoord(right_x, upper_mid_y),
            DisplayCoord(right_x, lower_mid_y),
            DisplayCoord(centre_x, bottom_y),
            DisplayCoord(left_x, lower_mid_y),
            DisplayCoord(left_x, upper_mid_y),
        )

    @classmethod
    def lr_directions(cls) -> dict[str, int]:
        return {
            "F": 1,
            "R": 2,
            "I": 3,  # rIght
            "B": 4,
            "E": 5,  # lEft
            "L": 6,
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

    def _validate_coord(self, coord: GridCoord) -> bool:
        # Only (odd, odd) or (even, even) coords are valid
        return coord.x % 2 == coord.y % 2

    @staticmethod
    def is_even(coord: GridCoord) -> bool:
        return coord.x % 2 == 0

    def get_neighbour(
        self, coord: GridCoord, direction: CardinalDirection
    ) -> GridCoord:
        self._check_coord(coord)
        # The above check also happens later in the super() call, but it probably
        # makes sense to catch it earlier to avoid misleading errors about invalid
        # directions for invalid coordinates.

        if direction not in self.directions:
            raise InvalidDirection(direction)

        valid_dirs = self._even_dirs if self.is_even(coord) else self._odd_dirs

        if direction not in valid_dirs:
            raise InvalidDirection(direction, coord)

        return super().get_neighbour(coord, direction)

    @classmethod
    def _get_cell_vertices(cls, coord: GridCoord) -> tuple[DisplayCoord, ...]:
        # TODO
        raise NotImplementedError

    @classmethod
    def lr_directions(cls) -> dict[str, int]:
        return {
            "R": 1,
            "B": 2,
            "L": 3,
        }

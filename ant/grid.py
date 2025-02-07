from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, NamedTuple, Generator, Any

from ant.types import AntColour, CardinalDirection, CellColour, Rule


class RuleKey(NamedTuple):
    ant_colour: AntColour
    cell_colour: CellColour


class AntState(NamedTuple):
    position: GridCoord
    direction: CardinalDirection
    colour: AntColour


class Ant:
    def __init__(
        self,
        grid: Grid,
        rules: Iterable[Rule],
        initial_state: AntState,
    ) -> None:
        self._grid = grid
        self._state = initial_state
        self._prev_position = initial_state.position

        self._rules: dict[RuleKey, Rule] = {}
        for rule in rules:
            key = RuleKey(ant_colour=rule.ant_colour, cell_colour=rule.cell_colour)
            if key in self._rules:
                print(f"Warning: duplicate rules for {key}")
            self._rules[key] = rule

        grid.add_ant(self)

    @property
    def grid(self) -> Grid:
        return self._grid

    def step(self) -> None:
        # Look up the rule
        rule_key = RuleKey(
            ant_colour=self.state.colour, cell_colour=self._grid[self.state.position]
        )
        rule = self._rules[rule_key]

        # change the colour of the current cell
        self._grid[self.state.position] = rule.new_cell_colour

        # calculate the new direction, then move the ant in that direction
        new_direction = self._grid.get_direction(
            self.state.position, self.state.direction, rule.turn
        )
        new_position = self._grid.get_neighbour(self.state.position, new_direction)

        self._prev_position = self.state.position
        self._state = AntState(
            position=new_position, direction=new_direction, colour=rule.new_ant_colour
        )

    @property
    def state(self) -> AntState:
        return self._state

    @property
    def prev_position(self) -> GridCoord:
        # Useful for drawing the ant, when we usually want to show where it just was
        return self._prev_position

    def __repr__(self) -> str:
        return f"Ant(state={self.state})"


@dataclass(frozen=True)
class Vector:
    dx: int
    dy: int

    def __add__(self, other: Vector) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented

        return Vector(self.dx + other.dx, self.dy + other.dy)

    def __radd__(self, other: Vector) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented

        return self + other


@dataclass(frozen=True)
class GridCoord:
    x: int
    y: int

    def __add__(self, vector: Vector) -> GridCoord:
        if not isinstance(vector, Vector):
            return NotImplemented

        return GridCoord(self.x + vector.dx, self.y + vector.dy)

    def __radd__(self, vector: Vector) -> GridCoord:
        if not isinstance(vector, Vector):
            return NotImplemented

        return self + vector


class DisplayCoord(NamedTuple):
    x: float
    y: float


class InvalidCoord(Exception):
    def __init__(self, coord: GridCoord) -> None:
        super().__init__(f"Invalid coordinate {coord}")


class InvalidDirection(Exception):
    def __init__(self, direction: CardinalDirection, coord: GridCoord) -> None:
        super().__init__(f"Bad direction {direction!r} for coord {coord}")


class Grid(ABC):
    """
    An unbounded grid, where each cell is coloured.

    All cells begin coloured in the default colour.

    We define:
        - North as negative Y
        - South as positive Y
        - East as positive X
        - West as negative X

    This fits with the typical coordinate systems used to draw on screen,
    where (0, 0) is in the top-left of the window, with positive Y going downwards,
    and positive X going right.
    """

    _cell_vertices_cache: dict[GridCoord, tuple[DisplayCoord, ...]]

    def __init__(
        self, default_colour: CellColour = CellColour(0), store_default: bool = False
    ) -> None:
        self._default_colour = default_colour
        self._store_default = store_default
        self._grid: dict[GridCoord, CellColour] = {}

        self._ants: list[Ant] = []

        # Used for the "fast" bbox (which does not take into account true grid geometry)
        self._has_data = False
        self._min_x: int = 0
        self._min_y: int = 0
        self._max_x: int = 0
        self._max_y: int = 0

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._cell_vertices_cache = {}

    def add_ant(self, ant: Ant) -> None:
        self._ants.append(ant)

    @property
    def ants(self) -> list[Ant]:
        return self._ants[:]

    def __contains__(self, coord: GridCoord) -> bool:
        self._check_coord(coord)
        return coord in self._grid

    def __getitem__(self, coord: GridCoord) -> CellColour:
        self._check_coord(coord)
        return self._grid.get(coord, self._default_colour)

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return self._min_x, self._min_y, self._max_x, self._max_y

    def __setitem__(self, coord: GridCoord, colour: CellColour) -> None:
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

    def __iter__(self) -> Generator[tuple[GridCoord, CellColour]]:
        for coord, colour in self._grid.items():
            yield coord, colour

    @classmethod
    def get_cell_vertices(cls, coord: GridCoord) -> tuple[DisplayCoord, ...]:
        """Returns the 2d coordinates of the cell's vertices, to be used for rendering."""
        try:
            display_coords = cls._cell_vertices_cache[coord]
        except KeyError:
            display_coords = cls._get_cell_vertices(coord)
            cls._cell_vertices_cache[coord] = display_coords
        return display_coords

    @classmethod
    @abstractmethod
    def get_ant_angle(cls, direction: CardinalDirection) -> int:
        """
        Returns the angle the ant is facing (in degrees) when pointing in the given direction.

        0 is north, 90 is east, 180 is south, 270 is west.
        """

    @classmethod
    @abstractmethod
    def _get_cell_vertices(cls, coord: GridCoord) -> tuple[DisplayCoord, ...]:
        pass

    @classmethod
    @abstractmethod
    def get_cell_centrepoint(cls, coord: GridCoord) -> DisplayCoord:
        """Returns the centre point of the cell, useful if we want to draw an ant on top"""
        pass

    def get_display_bbox(self) -> tuple[float, float, float, float]:
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

    @abstractmethod
    def get_direction_vectors(
        self, coord: GridCoord
    ) -> dict[CardinalDirection, Vector]:
        """Returns a mapping of directions to vectors for neighbours of the given grid coordinate."""

    def get_direction(
        self, coord: GridCoord, old_direction: CardinalDirection, turn: int
    ) -> CardinalDirection:
        # 1 is forward, 2 is first step clockwise and so on
        turn = turn - 1
        direction_vectors = self.get_direction_vectors(coord)
        directions = sorted(direction_vectors.keys())
        old_index = directions.index(old_direction)
        return directions[(old_index + turn) % len(direction_vectors)]

    def _check_coord(self, coord: GridCoord) -> None:
        if not self._validate_coord(coord):
            raise InvalidCoord(coord)

    def get_neighbour(
        self, coord: GridCoord, direction: CardinalDirection
    ) -> GridCoord:
        self._check_coord(coord)
        direction_vectors = self.get_direction_vectors(coord)
        if direction not in direction_vectors:
            raise InvalidDirection(direction, coord)
        return coord + direction_vectors[direction]

    def _validate_coord(self, coord: GridCoord) -> bool:
        # All coords are valid in square and hex grids
        return True

    @classmethod
    @abstractmethod
    def lr_directions(cls) -> dict[str, int]:
        pass

    @classmethod
    def _tokenise_lr_string(cls, lr_str: str) -> Generator[str]:
        # We want to match greedily, so longest keys first.
        # Note this does not handle cases where tokens can run into one another ambiguously
        # (even if that ambiguity is resolved in the string as a whole).
        valid_tokens = sorted(cls.lr_directions().keys(), key=len, reverse=True)

        lr_str_ = lr_str

        while lr_str_:
            for token in valid_tokens:
                if lr_str_.startswith(token):
                    yield token
                    lr_str_ = lr_str_[len(token) :]
                    break
            else:
                raise ValueError(
                    f"Invalid LR string: {lr_str}. Valid tokens: {valid_tokens}"
                )

    @classmethod
    def rules_from_lr_string(cls, lr_string: str) -> list[Rule]:
        # LR string rules are all in ant colour 0, and have one cell colour per character.
        ant_colour = AntColour(0)
        rules = []
        dirs = cls.lr_directions()

        rule_tokens = list(cls._tokenise_lr_string(lr_string))

        for colour, turn_dir in enumerate(rule_tokens):
            if turn_dir not in dirs:
                raise ValueError(f"Bad LR string value for {cls.__name__}: {turn_dir}")

            rules.append(
                Rule(
                    ant_colour=ant_colour,
                    cell_colour=CellColour(colour),
                    new_ant_colour=ant_colour,
                    new_cell_colour=CellColour((colour + 1) % len(rule_tokens)),
                    turn=dirs[turn_dir],
                )
            )

        for i, rule in enumerate(rules):
            print(i, rule)
        return rules


class SquareGrid(Grid):
    def get_direction_vectors(
        self, coord: GridCoord
    ) -> dict[CardinalDirection, Vector]:
        return {
            CardinalDirection.NORTH: Vector(0, -1),
            CardinalDirection.EAST: Vector(1, 0),
            CardinalDirection.SOUTH: Vector(0, 1),
            CardinalDirection.WEST: Vector(-1, 0),
        }

    @classmethod
    def get_ant_angle(cls, direction: CardinalDirection) -> int:
        match direction:
            case CardinalDirection.NORTH:
                return 0
            case CardinalDirection.EAST:
                return 90
            case CardinalDirection.SOUTH:
                return 180
            case CardinalDirection.WEST:
                return 270
            case _:
                raise ValueError(
                    f"Unsupported direction {direction} for {cls.__name__}"
                )

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
    def get_cell_centrepoint(cls, coord: GridCoord) -> DisplayCoord:
        return DisplayCoord(coord.x + 0.5, coord.y + 0.5)

    @classmethod
    def lr_directions(cls) -> dict[str, int]:
        # Synonyms:
        # F / N: Forwards / No change
        # B / U: Backwards / U-turn
        return {
            "F": 1,  # Forwards
            "N": 1,  # No change
            "R": 2,
            "B": 3,  # Backwards
            "U": 3,  # U-turn
            "L": 4,
        }


class HexGrid(Grid):
    # Handy: https://www.redblobgames.com/grids/hexagons/
    # This is a "pointy-topped" grid, ie cells lie in horizontal rows.

    #  /`\
    # | C |
    #  \./

    # We define centre to centre horizontally to be 1 unit.
    # Therefore the "size" of the hexagons (centre to any vertex) is 1/sqrt(3)
    SIZE = 3**-0.5

    _COMMON_VECTORS = {
        CardinalDirection.EAST: Vector(1, 0),
        CardinalDirection.WEST: Vector(-1, 0),
    }

    # Because our hex grid is just a square one in disguise, we must treat
    # every other row is offset by half a cell. This means our up and down
    # vectors differ depending on whether we're in an odd or even row.
    _EVEN_VECTORS = {
        CardinalDirection.NORTH_EAST: Vector(0, -1),
        CardinalDirection.SOUTH_EAST: Vector(0, 1),
        CardinalDirection.NORTH_WEST: Vector(-1, -1),
        CardinalDirection.SOUTH_WEST: Vector(-1, 1),
        **_COMMON_VECTORS,
    }
    _ODD_VECTORS = {
        CardinalDirection.NORTH_EAST: Vector(1, -1),
        CardinalDirection.SOUTH_EAST: Vector(1, 1),
        CardinalDirection.NORTH_WEST: Vector(0, -1),
        CardinalDirection.SOUTH_WEST: Vector(0, 1),
        **_COMMON_VECTORS,
    }

    def get_direction_vectors(
        self, coord: GridCoord
    ) -> dict[CardinalDirection, Vector]:
        return self._EVEN_VECTORS if coord.y % 2 == 0 else self._ODD_VECTORS

    @classmethod
    def get_ant_angle(cls, direction: CardinalDirection) -> int:
        match direction:
            case CardinalDirection.NORTH_EAST:
                return 30
            case CardinalDirection.EAST:
                return 90
            case CardinalDirection.SOUTH_EAST:
                return 150
            case CardinalDirection.SOUTH_WEST:
                return 210
            case CardinalDirection.WEST:
                return 270
            case CardinalDirection.NORTH_WEST:
                return 330
            case _:
                raise ValueError(
                    f"Unsupported direction {direction} for {cls.__name__}"
                )

    @classmethod
    def _get_cell_vertices(cls, coord: GridCoord) -> tuple[DisplayCoord, ...]:
        centre = cls.get_cell_centrepoint(coord)

        left_x = centre.x - 0.5
        right_x = centre.x + 0.5

        top_y = centre.y + cls.SIZE
        upper_mid_y = centre.y + cls.SIZE / 2
        lower_mid_y = centre.y - cls.SIZE / 2
        bottom_y = centre.y - cls.SIZE

        return (
            DisplayCoord(centre.x, top_y),
            DisplayCoord(right_x, upper_mid_y),
            DisplayCoord(right_x, lower_mid_y),
            DisplayCoord(centre.x, bottom_y),
            DisplayCoord(left_x, lower_mid_y),
            DisplayCoord(left_x, upper_mid_y),
        )

    @classmethod
    def get_cell_centrepoint(cls, coord: GridCoord) -> DisplayCoord:
        # Odd rows are offset by half
        centre_x = coord.x + (coord.y % 2) / 2
        centre_y = coord.y / (cls.SIZE * 2)

        return DisplayCoord(centre_x, centre_y)

    @classmethod
    def lr_directions(cls) -> dict[str, int]:
        # Synonymns:
        # F / N  -> Forwards / No change (0 degrees)
        # R / R1 -> Right 60 degrees
        # I / R2 -> rIght 120 degrees
        # B / U  -> Backwards / U-turn (180 degrees)
        # E / L2 -> lEft 120 degrees
        # L / L1 -> Left 60 degrees

        return {
            "F": 1,
            "N": 1,
            "R": 2,
            "R1": 2,
            "I": 3,  # rIght
            "R2": 3,
            "B": 4,
            "U": 4,
            "E": 5,  # lEft
            "L2": 5,
            "L": 6,
            "L1": 6,
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

    _HEIGHT = 3**0.5

    def get_direction_vectors(
        self, coord: GridCoord
    ) -> dict[CardinalDirection, Vector]:
        # TODO: check this
        if self.is_even(coord):
            return {
                CardinalDirection.NORTH_WEST: Vector(-1, 1),
                CardinalDirection.NORTH_EAST: Vector(1, 1),
                CardinalDirection.SOUTH: Vector(1, -1),
            }
        return {
            CardinalDirection.NORTH: Vector(-1, 1),
            CardinalDirection.SOUTH_EAST: Vector(1, -1),
            CardinalDirection.SOUTH_WEST: Vector(-1, -1),
        }

    def get_direction(
        self, coord: GridCoord, old_direction: CardinalDirection, turn: int
    ) -> CardinalDirection:
        if old_direction in self._even_dirs:
            old_dirs = self._even_dirs
            new_dirs = self._odd_dirs
        elif old_direction in self._odd_dirs:
            old_dirs = self._odd_dirs
            new_dirs = self._even_dirs
            turn = turn - 1
        else:
            raise InvalidDirection(old_direction, coord)

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

    @classmethod
    def get_ant_angle(cls, direction: CardinalDirection) -> int:
        match direction:
            case CardinalDirection.NORTH:
                return 0
            case CardinalDirection.NORTH_EAST:
                return 60
            case CardinalDirection.SOUTH_EAST:
                return 120
            case CardinalDirection.SOUTH:
                return 180
            case CardinalDirection.SOUTH_WEST:
                return 240
            case CardinalDirection.NORTH_WEST:
                return 300
            case _:
                raise ValueError(
                    f"Unsupported direction {direction} for {cls.__name__}"
                )

    def get_neighbour(
        self, coord: GridCoord, direction: CardinalDirection
    ) -> GridCoord:
        self._check_coord(coord)
        # The above check also happens later in the super() call, but it probably
        # makes sense to catch it earlier to avoid misleading errors about invalid
        # directions for invalid coordinates.

        direction_vectors = self.get_direction_vectors(coord)
        if direction not in direction_vectors:
            raise InvalidDirection(direction, coord)

        valid_dirs = self._even_dirs if self.is_even(coord) else self._odd_dirs

        if direction not in valid_dirs:
            raise InvalidDirection(direction, coord)

        return super().get_neighbour(coord, direction)

    @classmethod
    def _get_cell_vertices(cls, coord: GridCoord) -> tuple[DisplayCoord, ...]:
        # For display purposes, we define our triangles to have a side length of 2.
        # Height is therefore sqrt(3)

        # Even coords point towards positive Y.
        # Coord (0, 0) has left corner at (0, 0)
        # Coord (2, 0) has left corner at (2, 0)
        # Coord (0, 2) has left corner at (1, H)
        # Coord (x, y) has left corner at (y//2 + x, y//2 * H)

        if cls.is_even(coord):
            bottom_left = DisplayCoord(
                coord.x + coord.y // 2, coord.y // 2 * cls._HEIGHT
            )
            return (
                bottom_left,
                DisplayCoord(bottom_left.x + 2, bottom_left.y),
                DisplayCoord(bottom_left.x + 1, bottom_left.y + cls._HEIGHT),
            )

        # Odd coords point towards negative Y.
        # Coord (1, 1) has bottom corner at (2, 0)
        # Coord (3, 1) has bottom corner at (4, 0)
        # Coord (1, 3) has bottom corner at (3, h)
        # Coord (x, y) has bottom corner at (1 + x + y//2, y//2 * H)

        bottom = DisplayCoord(1 + coord.x + coord.y // 2, coord.y // 2 * cls._HEIGHT)

        return (
            bottom,
            DisplayCoord(bottom.x - 1, bottom.y + cls._HEIGHT),
            DisplayCoord(bottom.x + 1, bottom.y + cls._HEIGHT),
        )

    @classmethod
    def get_cell_centrepoint(cls, coord: GridCoord) -> DisplayCoord:
        # Side length is 2, so height is sqrt(2**2 - 1**2) == sqrt(3)
        if cls.is_even(coord):
            bot_left = cls.get_cell_vertices(coord)[0]
            return DisplayCoord(bot_left.x + 1, bot_left.y + cls._HEIGHT / 3)

        bottom = cls.get_cell_vertices(coord)[0]
        return DisplayCoord(bottom.x, bottom.y + cls._HEIGHT * 2 / 3)

    @classmethod
    def lr_directions(cls) -> dict[str, int]:
        return {
            "R": 1,
            "B": 2,
            "L": 3,
        }

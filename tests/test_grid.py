from contextlib import nullcontext as does_not_raise

import pytest

from ant.grid import (
    CardinalDirection,
    Coord,
    HexGrid,
    InvalidCoord,
    InvalidDirection,
    SquareGrid,
    TriangleGrid,
    Vector,
)


def test_adding_vectors_to_coords():
    coord = Coord(10, 10)
    vector = Vector(4, 1)
    expected = Coord(14, 11)
    assert coord + vector == expected
    assert vector + coord == expected


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_empty_grid_returns_default_value(grid_cls):
    grid = grid_cls()
    assert grid[Coord(0, 0)] == 0


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_empty_grid_returns_custom_default_value(grid_cls):
    grid = grid_cls(default_value=999)
    assert grid[Coord(123, 321)] == 999


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_saved_value_is_returned(grid_cls):
    grid = grid_cls()
    coord = Coord(10, 2)
    grid[coord] = 42
    assert grid[coord] == 42


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_iter(grid_cls):
    grid = grid_cls()
    grid[Coord(0, 0)] = 42
    grid[Coord(5, 5)] = 21

    assert {k: v for k, v in grid} == {Coord(0, 0): 42, Coord(5, 5): 21}


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_default_values_not_stored(grid_cls):
    grid = grid_cls()
    grid[Coord(0, 0)] = 42
    grid[Coord(5, 5)] = 21
    grid[Coord(5, 5)] = 0

    assert {k: v for k, v in grid} == {Coord(0, 0): 42}


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_custom_default_values_not_stored(grid_cls):
    grid = grid_cls(default_value=999)
    grid[Coord(0, 0)] = 42
    grid[Coord(5, 5)] = 21
    grid[Coord(5, 5)] = 999

    assert {k: v for k, v in grid} == {Coord(0, 0): 42}


@pytest.mark.parametrize(
    ["coord", "expectation"],
    [
        (Coord(0, 0), does_not_raise()),
        (Coord(-1, -1), does_not_raise()),
        (Coord(1, 0), pytest.raises(InvalidCoord)),
        (Coord(-1, 0), pytest.raises(InvalidCoord)),
        (Coord(-99999, 99999), does_not_raise()),
        (Coord(-99998, 99999), pytest.raises(InvalidCoord)),
    ],
)
def test_invalid_coords(coord, expectation):
    grid = TriangleGrid()
    with expectation:
        assert grid[coord] == 0


@pytest.mark.parametrize(
    ["grid_cls", "coord", "direction", "expectation", "new_coord"],
    # fmt: off
    [
        # Square grids only allow N, E, S, W
        (SquareGrid, Coord(1, -1), CardinalDirection.NORTH, does_not_raise(), Coord(1, 0)),
        (SquareGrid, Coord(1, -1), CardinalDirection.EAST, does_not_raise(), Coord(2, -1)),
        (SquareGrid, Coord(1, -1), CardinalDirection.SOUTH, does_not_raise(), Coord(1, -2)),
        (SquareGrid, Coord(1, -1), CardinalDirection.WEST, does_not_raise(), Coord(0, -1)),
        # Diagonals are not allowed
        (SquareGrid, Coord(1, -1), CardinalDirection.NORTH_EAST, pytest.raises(InvalidDirection), None),
        (SquareGrid, Coord(1, -1), CardinalDirection.SOUTH_EAST, pytest.raises(InvalidDirection), None),
        (SquareGrid, Coord(1, -1), CardinalDirection.SOUTH_WEST, pytest.raises(InvalidDirection), None),
        (SquareGrid, Coord(1, -1), CardinalDirection.NORTH_WEST, pytest.raises(InvalidDirection), None),
        # Hex grids have horizontal rows, so only N and S are disallowed
        (HexGrid, Coord(1, -1), CardinalDirection.EAST, does_not_raise(), Coord(2, -1)),
        (HexGrid, Coord(1, -1), CardinalDirection.WEST, does_not_raise(), Coord(0, -1)),
        (HexGrid, Coord(1, -1), CardinalDirection.NORTH_EAST, does_not_raise(), Coord(1, 0)),
        (HexGrid, Coord(1, -1), CardinalDirection.SOUTH_EAST, does_not_raise(), Coord(2, -2)),
        (HexGrid, Coord(1, -1), CardinalDirection.SOUTH_WEST, does_not_raise(), Coord(1, -2)),
        (HexGrid, Coord(1, -1), CardinalDirection.NORTH_WEST, does_not_raise(), Coord(0, 0)),
        (HexGrid, Coord(1, -1), CardinalDirection.NORTH, pytest.raises(InvalidDirection), None),
        (HexGrid, Coord(1, -1), CardinalDirection.SOUTH, pytest.raises(InvalidDirection), None),
        # Triangle grids allow different directions depending on whether the cell is odd or even
        # Odd cells:
        (TriangleGrid, Coord(1, -1), CardinalDirection.NORTH, does_not_raise(), Coord(0, 0)),
        (TriangleGrid, Coord(1, -1), CardinalDirection.SOUTH_WEST, does_not_raise(), Coord(0, -2)),
        (TriangleGrid, Coord(1, -1), CardinalDirection.SOUTH_EAST, does_not_raise(), Coord(2, -2)),
        (TriangleGrid, Coord(1, -1), CardinalDirection.EAST, pytest.raises(InvalidDirection), None),
        (TriangleGrid, Coord(1, -1), CardinalDirection.SOUTH, pytest.raises(InvalidDirection), None),
        (TriangleGrid, Coord(1, -1), CardinalDirection.WEST, pytest.raises(InvalidDirection), None),
        (TriangleGrid, Coord(1, -1), CardinalDirection.NORTH_EAST, pytest.raises(InvalidDirection), None),
        (TriangleGrid, Coord(1, -1), CardinalDirection.NORTH_WEST, pytest.raises(InvalidDirection), None),
        # Even cells:
        (TriangleGrid, Coord(2, 0), CardinalDirection.NORTH_WEST, does_not_raise(), Coord(1, 1)),
        (TriangleGrid, Coord(2, 0), CardinalDirection.NORTH_EAST, does_not_raise(), Coord(3, 1)),
        (TriangleGrid, Coord(2, 0), CardinalDirection.SOUTH, does_not_raise(), Coord(3, -1)),
        (TriangleGrid, Coord(2, 0), CardinalDirection.NORTH, pytest.raises(InvalidDirection), None),
        (TriangleGrid, Coord(2, 0), CardinalDirection.EAST, pytest.raises(InvalidDirection), None),
        (TriangleGrid, Coord(2, 0), CardinalDirection.WEST, pytest.raises(InvalidDirection), None),
        (TriangleGrid, Coord(2, 0), CardinalDirection.SOUTH_EAST, pytest.raises(InvalidDirection), None),
        (TriangleGrid, Coord(2, 0), CardinalDirection.SOUTH_WEST, pytest.raises(InvalidDirection), None),
    ],
    # fmt: on
)
def test_directions(grid_cls, coord, direction, expectation, new_coord):
    grid = grid_cls()
    with expectation:
        assert grid.get_neighbour(coord, direction) == new_coord

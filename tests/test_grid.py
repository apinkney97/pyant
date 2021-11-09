from contextlib import nullcontext as does_not_raise

import pytest

from ant.grid import (
    CardinalDirection,
    Colour,
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
    some_colour = Colour(999)
    grid = grid_cls(default_colour=some_colour)
    assert grid[Coord(123, 321)] == some_colour


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_saved_value_is_returned(grid_cls):
    grid = grid_cls()
    coord = Coord(10, 2)
    some_colour = Colour(42)
    grid[coord] = some_colour
    assert grid[coord] == some_colour


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_iter(grid_cls):
    grid = grid_cls()

    some_colour = Colour(42)
    other_colour = Colour(21)

    grid[Coord(0, 0)] = some_colour
    grid[Coord(5, 5)] = other_colour

    assert {k: v for k, v in grid} == {
        Coord(0, 0): some_colour,
        Coord(5, 5): other_colour,
    }


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_default_values_not_stored(grid_cls):
    grid = grid_cls()

    some_colour = Colour(42)
    other_colour = Colour(21)

    grid[Coord(0, 0)] = some_colour
    grid[Coord(5, 5)] = other_colour
    grid[Coord(5, 5)] = Colour(0)

    assert {k: v for k, v in grid} == {Coord(0, 0): some_colour}


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_custom_default_values_not_stored(grid_cls):
    default_colour = Colour(999)
    some_colour = Colour(42)
    other_colour = Colour(21)

    grid = grid_cls(default_colour=default_colour)

    grid[Coord(0, 0)] = some_colour
    grid[Coord(5, 5)] = other_colour
    grid[Coord(5, 5)] = default_colour

    assert {k: v for k, v in grid} == {Coord(0, 0): some_colour}


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


@pytest.mark.parametrize(
    ["grid_cls", "old_dir", "turn", "expected_new_dir"],
    [
        (SquareGrid, CardinalDirection.NORTH, 1, CardinalDirection.NORTH),
        (SquareGrid, CardinalDirection.EAST, 1, CardinalDirection.EAST),
        (SquareGrid, CardinalDirection.SOUTH, 1, CardinalDirection.SOUTH),
        (SquareGrid, CardinalDirection.WEST, 1, CardinalDirection.WEST),
        (SquareGrid, CardinalDirection.WEST, 3, CardinalDirection.EAST),
        (SquareGrid, CardinalDirection.WEST, 4, CardinalDirection.SOUTH),
        (HexGrid, CardinalDirection.EAST, 1, CardinalDirection.EAST),
        (HexGrid, CardinalDirection.WEST, 1, CardinalDirection.WEST),
        (HexGrid, CardinalDirection.NORTH_EAST, 1, CardinalDirection.NORTH_EAST),
        (HexGrid, CardinalDirection.SOUTH_EAST, 1, CardinalDirection.SOUTH_EAST),
        (HexGrid, CardinalDirection.SOUTH_WEST, 1, CardinalDirection.SOUTH_WEST),
        (HexGrid, CardinalDirection.NORTH_WEST, 1, CardinalDirection.NORTH_WEST),
        (HexGrid, CardinalDirection.EAST, 2, CardinalDirection.SOUTH_EAST),
        (HexGrid, CardinalDirection.EAST, 3, CardinalDirection.SOUTH_WEST),
        (HexGrid, CardinalDirection.EAST, 4, CardinalDirection.WEST),
        (HexGrid, CardinalDirection.EAST, 5, CardinalDirection.NORTH_WEST),
        (HexGrid, CardinalDirection.EAST, 6, CardinalDirection.NORTH_EAST),
        (TriangleGrid, CardinalDirection.NORTH, 1, CardinalDirection.NORTH_EAST),
        (TriangleGrid, CardinalDirection.NORTH, 2, CardinalDirection.SOUTH),
        (TriangleGrid, CardinalDirection.NORTH, 3, CardinalDirection.NORTH_WEST),
        (TriangleGrid, CardinalDirection.SOUTH_EAST, 1, CardinalDirection.SOUTH),
        (TriangleGrid, CardinalDirection.SOUTH_WEST, 1, CardinalDirection.NORTH_WEST),
        (TriangleGrid, CardinalDirection.NORTH_EAST, 1, CardinalDirection.SOUTH_EAST),
        (TriangleGrid, CardinalDirection.SOUTH, 1, CardinalDirection.SOUTH_WEST),
        (TriangleGrid, CardinalDirection.NORTH_WEST, 1, CardinalDirection.NORTH),
    ],
)
def test_get_direction(grid_cls, old_dir, turn, expected_new_dir):
    grid = grid_cls()

    assert grid.get_direction(old_dir, turn) == expected_new_dir

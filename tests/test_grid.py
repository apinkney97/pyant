from contextlib import nullcontext as does_not_raise

import pytest

from ant.grid import (
    DisplayCoord,
    GridCoord,
    HexGrid,
    InvalidCoord,
    InvalidDirection,
    SquareGrid,
    TriangleGrid,
    Vector,
)
from ant.types import AntColour, CellColour, Rule, CardinalDirection


def test_adding_vectors_to_coords():
    coord = GridCoord(10, 10)
    vector = Vector(4, 1)
    expected = GridCoord(14, 11)
    assert coord + vector == expected
    assert vector + coord == expected


def test_adding_vectors_to_vectors():
    vector_1 = Vector(2, 5)
    vector_2 = Vector(8, 5)

    expected = Vector(10, 10)
    assert vector_1 + vector_2 == expected
    assert vector_2 + vector_1 == expected


def test_adding_coords_fails():
    coord_1 = GridCoord(1, 1)
    coord_2 = GridCoord(9, 9)

    with pytest.raises(TypeError):
        coord_1 + coord_2


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_empty_grid_returns_default_value(grid_cls):
    grid = grid_cls()
    assert grid[GridCoord(0, 0)] == 0


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_empty_grid_returns_custom_default_value(grid_cls):
    some_colour = CellColour(999)
    grid = grid_cls(default_colour=some_colour)
    assert grid[GridCoord(123, 321)] == some_colour


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_saved_value_is_returned(grid_cls):
    grid = grid_cls()
    coord = GridCoord(10, 2)
    some_colour = CellColour(42)
    grid[coord] = some_colour
    assert grid[coord] == some_colour


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_iter(grid_cls):
    grid = grid_cls()

    some_colour = CellColour(42)
    other_colour = CellColour(21)

    grid[GridCoord(0, 0)] = some_colour
    grid[GridCoord(5, 5)] = other_colour

    assert {k: v for k, v in grid} == {
        GridCoord(0, 0): some_colour,
        GridCoord(5, 5): other_colour,
    }


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_default_values_not_stored(grid_cls):
    grid = grid_cls()

    some_colour = CellColour(42)
    other_colour = CellColour(21)

    grid[GridCoord(0, 0)] = some_colour
    grid[GridCoord(5, 5)] = other_colour
    grid[GridCoord(5, 5)] = CellColour(0)

    assert {k: v for k, v in grid} == {GridCoord(0, 0): some_colour}


@pytest.mark.parametrize(["grid_cls"], [(TriangleGrid,), (SquareGrid,), (HexGrid,)])
def test_custom_default_values_not_stored(grid_cls):
    default_colour = CellColour(999)
    some_colour = CellColour(42)
    other_colour = CellColour(21)

    grid = grid_cls(default_colour=default_colour)

    grid[GridCoord(0, 0)] = some_colour
    grid[GridCoord(5, 5)] = other_colour
    grid[GridCoord(5, 5)] = default_colour

    assert {k: v for k, v in grid} == {GridCoord(0, 0): some_colour}


@pytest.mark.parametrize(
    ["coord", "expectation"],
    [
        (GridCoord(0, 0), does_not_raise()),
        (GridCoord(-1, -1), does_not_raise()),
        (GridCoord(1, 0), pytest.raises(InvalidCoord)),
        (GridCoord(-1, 0), pytest.raises(InvalidCoord)),
        (GridCoord(-99999, 99999), does_not_raise()),
        (GridCoord(-99998, 99999), pytest.raises(InvalidCoord)),
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
        (SquareGrid, GridCoord(1, -1), CardinalDirection.NORTH, does_not_raise(), GridCoord(1, 0)),
        (SquareGrid, GridCoord(1, -1), CardinalDirection.EAST, does_not_raise(), GridCoord(2, -1)),
        (SquareGrid, GridCoord(1, -1), CardinalDirection.SOUTH, does_not_raise(), GridCoord(1, -2)),
        (SquareGrid, GridCoord(1, -1), CardinalDirection.WEST, does_not_raise(), GridCoord(0, -1)),
        # Diagonals are not allowed
        (SquareGrid, GridCoord(1, -1), CardinalDirection.NORTH_EAST, pytest.raises(InvalidDirection), None),
        (SquareGrid, GridCoord(1, -1), CardinalDirection.SOUTH_EAST, pytest.raises(InvalidDirection), None),
        (SquareGrid, GridCoord(1, -1), CardinalDirection.SOUTH_WEST, pytest.raises(InvalidDirection), None),
        (SquareGrid, GridCoord(1, -1), CardinalDirection.NORTH_WEST, pytest.raises(InvalidDirection), None),
        # Hex grids have horizontal rows, so only N and S are disallowed
        (HexGrid, GridCoord(1, -1), CardinalDirection.EAST, does_not_raise(), GridCoord(2, -1)),
        (HexGrid, GridCoord(1, -1), CardinalDirection.WEST, does_not_raise(), GridCoord(0, -1)),
        (HexGrid, GridCoord(1, -1), CardinalDirection.NORTH_EAST, does_not_raise(), GridCoord(1, 0)),
        (HexGrid, GridCoord(1, -1), CardinalDirection.SOUTH_EAST, does_not_raise(), GridCoord(2, -2)),
        (HexGrid, GridCoord(1, -1), CardinalDirection.SOUTH_WEST, does_not_raise(), GridCoord(1, -2)),
        (HexGrid, GridCoord(1, -1), CardinalDirection.NORTH_WEST, does_not_raise(), GridCoord(0, 0)),
        (HexGrid, GridCoord(1, -1), CardinalDirection.NORTH, pytest.raises(InvalidDirection), None),
        (HexGrid, GridCoord(1, -1), CardinalDirection.SOUTH, pytest.raises(InvalidDirection), None),
        # Triangle grids allow different directions depending on whether the cell is odd or even
        # Odd cells:
        (TriangleGrid, GridCoord(1, -1), CardinalDirection.NORTH, does_not_raise(), GridCoord(0, 0)),
        (TriangleGrid, GridCoord(1, -1), CardinalDirection.SOUTH_WEST, does_not_raise(), GridCoord(0, -2)),
        (TriangleGrid, GridCoord(1, -1), CardinalDirection.SOUTH_EAST, does_not_raise(), GridCoord(2, -2)),
        (TriangleGrid, GridCoord(1, -1), CardinalDirection.EAST, pytest.raises(InvalidDirection), None),
        (TriangleGrid, GridCoord(1, -1), CardinalDirection.SOUTH, pytest.raises(InvalidDirection), None),
        (TriangleGrid, GridCoord(1, -1), CardinalDirection.WEST, pytest.raises(InvalidDirection), None),
        (TriangleGrid, GridCoord(1, -1), CardinalDirection.NORTH_EAST, pytest.raises(InvalidDirection), None),
        (TriangleGrid, GridCoord(1, -1), CardinalDirection.NORTH_WEST, pytest.raises(InvalidDirection), None),
        # Even cells:
        (TriangleGrid, GridCoord(2, 0), CardinalDirection.NORTH_WEST, does_not_raise(), GridCoord(1, 1)),
        (TriangleGrid, GridCoord(2, 0), CardinalDirection.NORTH_EAST, does_not_raise(), GridCoord(3, 1)),
        (TriangleGrid, GridCoord(2, 0), CardinalDirection.SOUTH, does_not_raise(), GridCoord(3, -1)),
        (TriangleGrid, GridCoord(2, 0), CardinalDirection.NORTH, pytest.raises(InvalidDirection), None),
        (TriangleGrid, GridCoord(2, 0), CardinalDirection.EAST, pytest.raises(InvalidDirection), None),
        (TriangleGrid, GridCoord(2, 0), CardinalDirection.WEST, pytest.raises(InvalidDirection), None),
        (TriangleGrid, GridCoord(2, 0), CardinalDirection.SOUTH_EAST, pytest.raises(InvalidDirection), None),
        (TriangleGrid, GridCoord(2, 0), CardinalDirection.SOUTH_WEST, pytest.raises(InvalidDirection), None),
    ],
    # fmt: on
)
def test_directions(grid_cls, coord, direction, expectation, new_coord):
    grid = grid_cls()
    with expectation:
        assert grid.get_neighbour(coord, direction) == new_coord


@pytest.mark.skip("TODO: Add coord to get_direction call")
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


@pytest.mark.parametrize(
    ["grid_cls", "grid_coord", "expected_display_coords"],
    [
        (
            SquareGrid,
            GridCoord(5, 5),
            (
                DisplayCoord(5, 6),
                DisplayCoord(6, 6),
                DisplayCoord(6, 5),
                DisplayCoord(5, 5),
            ),
        ),
        (
            HexGrid,
            GridCoord(0, 0),
            (
                DisplayCoord(0.0, 0.5773502691896257),
                DisplayCoord(0.5, 0.28867513459481287),
                DisplayCoord(0.5, -0.28867513459481287),
                DisplayCoord(0.0, -0.5773502691896257),
                DisplayCoord(-0.5, -0.28867513459481287),
                DisplayCoord(-0.5, 0.28867513459481287),
            ),
        ),
        (
            HexGrid,
            GridCoord(1, 0),
            (
                DisplayCoord(1.0, 0.5773502691896257),
                DisplayCoord(1.5, 0.28867513459481287),
                DisplayCoord(1.5, -0.28867513459481287),
                DisplayCoord(1.0, -0.5773502691896257),
                DisplayCoord(0.5, -0.28867513459481287),
                DisplayCoord(0.5, 0.28867513459481287),
            ),
        ),
        (
            HexGrid,
            GridCoord(0, 1),
            (
                DisplayCoord(0.5, 1.4433756729740645),
                DisplayCoord(1.0, 1.1547005383792515),
                DisplayCoord(1.0, 0.5773502691896258),
                DisplayCoord(0.5, 0.288675134594813),
                DisplayCoord(0.0, 0.5773502691896258),
                DisplayCoord(0.0, 1.1547005383792515),
            ),
        ),
        (
            HexGrid,
            GridCoord(1, 1),
            (
                DisplayCoord(1.5, 1.4433756729740645),
                DisplayCoord(2.0, 1.1547005383792515),
                DisplayCoord(2.0, 0.5773502691896258),
                DisplayCoord(1.5, 0.288675134594813),
                DisplayCoord(1.0, 0.5773502691896258),
                DisplayCoord(1.0, 1.1547005383792515),
            ),
        ),
    ],
)
def test_get_cell_vertices(grid_cls, grid_coord, expected_display_coords):
    assert grid_cls.get_cell_vertices(grid_coord) == expected_display_coords


@pytest.mark.parametrize(
    ["grid_cls", "grid_coords", "expected_bbox"],
    [
        (
            SquareGrid,
            [],
            (0, 0, 0, 0),
        ),
        (
            SquareGrid,
            [GridCoord(0, 0)],
            (0, 0, 1, 1),
        ),
        (
            SquareGrid,
            [GridCoord(0, 0), GridCoord(5, 5)],
            (0, 0, 6, 6),
        ),
        (
            SquareGrid,
            [GridCoord(0, 0), GridCoord(-1, -1), GridCoord(5, 5)],
            (-1, -1, 6, 6),
        ),
        (
            HexGrid,
            [],
            (0, 0, 0, 0),
        ),
        (
            HexGrid,
            [GridCoord(0, 0)],
            (-0.5, -0.5773502691896257, 0.5, 0.5773502691896257),
        ),
        (
            HexGrid,
            [GridCoord(0, 0), GridCoord(5, 5)],
            (-0.5, -0.5773502691896257, 6.0, 4.907477288111819),
        ),
        (
            HexGrid,
            [GridCoord(0, 0), GridCoord(-1, -1), GridCoord(5, 5)],
            (-1.0, -1.4433756729740645, 6.0, 4.907477288111819),
        ),
    ],
)
def test_get_display_bbox(grid_cls, grid_coords, expected_bbox):
    grid = grid_cls()
    for coord in grid_coords:
        grid[coord] = CellColour(1)

    assert grid.get_display_bbox() == expected_bbox


@pytest.mark.parametrize(
    ["grid_cls", "lr_string", "expected"],
    [
        (
            SquareGrid,
            "LR",
            [
                Rule(
                    ant_colour=AntColour(0),
                    cell_colour=CellColour(0),
                    new_ant_colour=AntColour(0),
                    new_cell_colour=CellColour(1),
                    turn=4,
                ),
                Rule(
                    ant_colour=AntColour(0),
                    cell_colour=CellColour(1),
                    new_ant_colour=AntColour(0),
                    new_cell_colour=CellColour(0),
                    turn=2,
                ),
            ],
        ),
        (
            SquareGrid,
            "rl",
            [
                Rule(
                    ant_colour=AntColour(0),
                    cell_colour=CellColour(0),
                    new_ant_colour=AntColour(0),
                    new_cell_colour=CellColour(1),
                    turn=2,
                ),
                Rule(
                    ant_colour=AntColour(0),
                    cell_colour=CellColour(1),
                    new_ant_colour=AntColour(0),
                    new_cell_colour=CellColour(0),
                    turn=4,
                ),
            ],
        ),
        (
            SquareGrid,
            "Rrl",
            [
                Rule(
                    ant_colour=AntColour(0),
                    cell_colour=CellColour(0),
                    new_ant_colour=AntColour(0),
                    new_cell_colour=CellColour(1),
                    turn=2,
                ),
                Rule(
                    ant_colour=AntColour(0),
                    cell_colour=CellColour(1),
                    new_ant_colour=AntColour(0),
                    new_cell_colour=CellColour(2),
                    turn=2,
                ),
                Rule(
                    ant_colour=AntColour(0),
                    cell_colour=CellColour(2),
                    new_ant_colour=AntColour(0),
                    new_cell_colour=CellColour(0),
                    turn=4,
                ),
            ],
        ),
    ],
)
def test_rules_from_lr_string(grid_cls, lr_string, expected):
    assert grid_cls.rules_from_lr_string(lr_string) == expected

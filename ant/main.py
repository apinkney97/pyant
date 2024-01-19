import time
from itertools import count
from enum import StrEnum, auto

import typer
from graphics import tk  # type: ignore

from ant.ant import Ant
from ant.display import Display
from ant.grid import (
    CardinalDirection,
    Grid,
    GridCoord,
    HexGrid,
    SquareGrid,
    TriangleGrid,
)
from ant.types import AntState, Rule


class GridType(StrEnum):
    SQUARE = auto()
    HEX = auto()
    TRIANGLE = auto()


def make_ant(
    rules: str | list[Rule],
    grid: Grid | None = None,
    start_position: GridCoord = GridCoord(0, 0),
    start_direction: CardinalDirection = CardinalDirection.NORTH,
    ant_state: AntState = AntState(0),
) -> Ant:
    if grid is None:
        grid = SquareGrid(store_default=True)
    if isinstance(rules, str):
        rules = grid.rules_from_lr_string(rules)
    return Ant(
        grid=grid,
        rules=rules,
        position=start_position,
        direction=start_direction,
        state=ant_state,
    )


def validate_ants(ants: list[Ant]) -> Grid:
    # Validates all ants live on the same grid
    grid = ants[0].grid

    for ant in ants[1:]:
        if ant.grid is not grid:
            raise ValueError("Ant must all live on the same grid")
    return grid


def _run_live(
    ants: list[Ant],
    step_limit: int,
    sleep_interval: float,
    steps_per_redraw: int,
    size_limit: int,
) -> None:
    if not ants:
        return

    grid = validate_ants(ants)

    display = Display(grid)

    print("Use Ctrl-C to halt execution")

    wait = True

    range_ = range(step_limit) if step_limit else count()
    i = 0
    for i in range_:
        try:
            for ant in ants:
                ant.step()
            if i % steps_per_redraw == 0:
                display.render()
                display.set_title(f"Ant: {i}")
                if sleep_interval:
                    time.sleep(sleep_interval)
                if size_limit:
                    xmin, ymin, xmax, ymax = grid.bbox
                    if xmax - xmin > size_limit or ymax - ymin > size_limit:
                        print(f"Exceeded maximum size {size_limit} after {i} steps")
                        break
        except KeyboardInterrupt:
            display.render()  # In case we interrupted it
            display.set_title(f"Ant: {i}")
            print()
            break
        except tk.TclError:
            # Handle the window being closed
            wait = False
            break
    else:
        print(f"Ran for {i} steps")

    if wait:
        input("Hit enter to exit")


def _run(
    ants: list[Ant],
    step_limit: int,
    size_limit: int,
    title: str = "",
):
    grid = validate_ants(ants)
    for i in range(step_limit):
        for ant in ants:
            ant.step()
        if i % 10_000 == 0:
            min_x, min_y, max_x, max_y = grid.bbox
            if max_x - min_x > size_limit or max_y - min_y > size_limit:
                break
            print(f"After {i} steps, bbox: {grid.get_display_bbox()}")

    # TODO: Dump as PNG


app = typer.Typer()


@app.command()
def run(
    lr_rules: list[str],
    grid: GridType = GridType.SQUARE,
    steps_per_redraw: int = 10_000,
    sleep_interval: float = 0.0,
    step_limit: int = 1_000_000,
    size_limit: int = 1_000,
):
    grid_: Grid

    match grid:
        case GridType.SQUARE:
            grid_ = SquareGrid()
        case GridType.HEX:
            grid_ = HexGrid()
        case GridType.TRIANGLE:
            grid_ = TriangleGrid()
        case _:
            raise ValueError(f"Unhandled grid type {grid}")

    start_direction = CardinalDirection.NORTH
    if grid is GridType.HEX:
        start_direction = CardinalDirection.NORTH_WEST

    ants = []
    for rules in lr_rules:
        ants.append(make_ant(rules, grid_, start_direction=start_direction))

    _run_live(
        ants=ants,
        steps_per_redraw=steps_per_redraw,
        sleep_interval=sleep_interval,
        step_limit=step_limit,
        size_limit=size_limit,
    )


@app.command()
def dump():
    pass


def main():
    app()


if __name__ == "__main__":
    main()

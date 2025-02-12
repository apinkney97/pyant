import time
from enum import StrEnum, auto
from itertools import count

import typer
from graphics import tk  # type: ignore

from ant.display import Display
from ant.grid import Grid, HexGrid, SquareGrid, TriangleGrid
from ant.types import CardinalDirection


class GridType(StrEnum):
    SQUARE = auto()
    HEX = auto()
    TRIANGLE = auto()


def _run_live(
    grid: Grid,
    step_limit: int,
    sleep_interval: float,
    steps_per_redraw: int,
    size_limit: int,
    manual_steps: int,
) -> None:
    if not grid.ants:
        return

    display = Display(grid)

    print("Use Ctrl-C to halt execution")

    wait = True

    if manual_steps:
        steps_per_redraw = min(manual_steps, steps_per_redraw)

    range_ = iter(range(step_limit + 1) if step_limit else count())
    i = next(range_)
    for i in range_:
        try:
            for ant in grid.ants:
                ant.step(grid)
            manual_step = bool(manual_steps and i % manual_steps == 0)
            if i % steps_per_redraw == 0 or manual_step:
                display.render()
                display.set_title(f"Ant: {i}")
                if sleep_interval:
                    time.sleep(sleep_interval)
                if size_limit:
                    bbox = grid.get_display_bbox()
                    if (
                        bbox.max.x - bbox.min.x > size_limit
                        or bbox.max.y - bbox.min.y > size_limit
                    ):
                        print(f"Exceeded maximum size {size_limit} after {i} steps")
                        break
                if manual_step:
                    input(f"Step {i}; hit enter to continue")
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
    grid: Grid,
    step_limit: int,
    size_limit: int,
    title: str = "",
) -> None:
    for i in range(step_limit):
        for ant in grid.ants:
            ant.step(grid)
        if i % 10_000 == 0:
            bbox = grid.get_display_bbox()
            if (
                bbox.max.x - bbox.min.x > size_limit
                or bbox.max.y - bbox.min.y > size_limit
            ):
                break
            print(f"After {i} steps, bbox: {grid.get_display_bbox()}")

    # TODO: Dump as PNG


app = typer.Typer()


@app.command(help="Run live")
def run(
    lr_rules: list[str],
    grid: GridType = GridType.SQUARE,
    steps_per_redraw: int = 10_000,
    sleep_interval: float = 0.0,
    step_limit: int = 1_000_000,
    size_limit: int = 1_000,
    manual_steps: int = 0,
) -> None:
    grid_: Grid

    match grid:
        case GridType.SQUARE:
            grid_ = SquareGrid(store_default=True)
            start_direction = CardinalDirection.NORTH
        case GridType.HEX:
            grid_ = HexGrid(store_default=True)
            start_direction = CardinalDirection.NORTH_WEST
        case GridType.TRIANGLE:
            grid_ = TriangleGrid(store_default=True)
            start_direction = CardinalDirection.SOUTH
        case _:
            raise ValueError(f"Unhandled grid type {grid}")

    for rules in lr_rules:
        grid_.add_ant(rules, start_direction=start_direction)

    _run_live(
        grid=grid_,
        steps_per_redraw=steps_per_redraw,
        sleep_interval=sleep_interval,
        step_limit=step_limit,
        size_limit=size_limit,
        manual_steps=manual_steps,
    )


@app.command(help="Dump frames to image files")
def dump() -> None:
    for i, rules in enumerate(SquareGrid.all_rule_strings()):
        print(i, rules)
        if len(rules) > 10:
            break


def main() -> None:
    app()


if __name__ == "__main__":
    main()

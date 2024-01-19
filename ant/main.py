import time
from itertools import count

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


def lr_square_two() -> list[Ant]:
    grid = SquareGrid(store_default=True)
    ants = [
        make_ant(rules="LR", grid=grid),
        make_ant(rules="LR", grid=grid),
    ]
    return ants


def lr_square(rules: str = "LR") -> list[Ant]:
    return [make_ant(rules=rules)]


def lr_tri(rules: str = "LR") -> list[Ant]:
    return [make_ant(grid=TriangleGrid(store_default=True), rules=rules)]


def lr_hex(rules: str = "LR") -> list[Ant]:
    return [
        make_ant(
            grid=HexGrid(store_default=True),
            rules=rules,
            start_direction=CardinalDirection.NORTH_WEST,
        )
    ]


def validate_ants(ants: list[Ant]) -> Grid:
    # Validates all ants live on the same grid
    grid = ants[0].grid

    for ant in ants[1:]:
        if ant.grid is not grid:
            raise ValueError("Ant must all live on the same grid")
    return grid


def run_live(
    ants: list[Ant],
    step_limit: int = 0,
    sleep_interval: float = 0.0,
    steps_per_redraw: int = 1,
    size_limit: int = 1000,
) -> None:
    if not ants:
        return

    grid = validate_ants(ants)

    display = Display(grid)

    range_ = range(step_limit) if step_limit else count()
    for i in range_:
        try:
            for ant in ants:
                ant.step()
            if i % steps_per_redraw == 0:
                display.render()
                display.set_title(f"Ant: {i+1}")
                if sleep_interval:
                    time.sleep(sleep_interval)
                if size_limit:
                    xmin, ymin, xmax, ymax = grid.bbox
                    if xmax - xmin > size_limit or ymax - ymin > size_limit:
                        break
        except KeyboardInterrupt:
            display.render()  # In case we interrupted it
            print()
            break

    input("Hit enter to continue")


def run(
    ants: list[Ant],
    step_limit: int = 1_000_000,
    size_limit: int = 2000,
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


def main():
    limit = 0
    jump = 0
    pause = 0

    jump = 1000
    # pause = 0.2
    # limit = 13000

    # ants = lr_square()
    # ants = lr_square_two()
    ants = lr_hex("LR")
    # ants = lr_tri()

    # run_live(ants=ants, steps_per_redraw=jump, sleep_interval=pause, step_limit=limit)
    run(ants=ants, step_limit=50, title="something")


if __name__ == "__main__":
    main()

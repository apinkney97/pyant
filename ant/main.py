import time
from itertools import count

from ant.ant import Ant
from ant.display import Display
from ant.grid import CardinalDirection, GridCoord, HexGrid, SquareGrid
from ant.types import AntState


def lr_square_two() -> list[Ant]:
    grid = SquareGrid(store_default=True)
    rules = grid.rules_from_lr_string("LR")
    ant = Ant(
        rules=rules,
        grid=grid,
        position=GridCoord(0, 0),
        direction=CardinalDirection.WEST,
        state=AntState(0),
    )

    ant2 = Ant(
        rules=rules,
        grid=grid,
        position=GridCoord(10, 10),
        direction=CardinalDirection.EAST,
        state=AntState(0),
    )

    return [ant, ant2]


def lr_square() -> list[Ant]:
    grid = SquareGrid(store_default=True)
    rules = grid.rules_from_lr_string("LR")
    ant = Ant(
        rules=rules,
        grid=grid,
        position=GridCoord(0, 0),
        direction=CardinalDirection.WEST,
        state=AntState(0),
    )
    return [ant]


def lr_hex() -> list[Ant]:
    grid = HexGrid(store_default=True)
    rules = grid.rules_from_lr_string("LR")
    ant = Ant(
        rules=rules,
        grid=grid,
        position=GridCoord(0, 0),
        direction=CardinalDirection.WEST,
        state=AntState(0),
    )
    return [ant]


def run(
    *ants: Ant,
    step_limit: int = 0,
    sleep_interval: float = 0.0,
    steps_per_redraw: int = 1,
) -> None:
    if not ants:
        return

    grid = ants[0].grid

    for ant in ants[1:]:
        if ant.grid is not grid:
            raise ValueError("Ant must all live on the same grid")

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
        except KeyboardInterrupt:
            display.render()  # In case we interrupted it
            print()
            break

    input("Hit enter to continue")


def main():
    limit = 0
    jump = 0
    pause = 0

    jump = 1000
    # pause = 0.2
    # limit = 13000

    ants = lr_square()
    # ants = lr_hex()

    run(*ants, steps_per_redraw=jump, sleep_interval=pause, step_limit=limit)


if __name__ == "__main__":
    main()

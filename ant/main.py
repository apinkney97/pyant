import time

from ant.ant import Ant, AntState, Colour, Rule
from ant.display import Display
from ant.grid import CardinalDirection, GridCoord, SquareGrid


def main():
    grid = SquareGrid(store_default=True)
    rules = [
        Rule(
            state=AntState(0),
            colour=Colour(0),
            new_state=AntState(0),
            new_colour=Colour(1),
            turn=2,
        ),
        Rule(
            state=AntState(0),
            colour=Colour(1),
            new_state=AntState(0),
            new_colour=Colour(0),
            turn=4,
        ),
    ]
    ant = Ant(
        rules=rules,
        grid=grid,
        position=GridCoord(0, 0),
        direction=CardinalDirection.NORTH,
        state=AntState(0),
    )

    display = Display(grid)
    for _ in range(500):
        ant.step()
        display.render()
        # time.sleep(0.1)


if __name__ == "__main__":
    main()

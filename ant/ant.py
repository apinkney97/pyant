from typing import Iterable, NamedTuple

from ant.grid import CardinalDirection, Grid, GridCoord
from ant.types import AntState, Colour, Rule


class RuleKey(NamedTuple):
    state: AntState
    colour: Colour


class Ant:
    def __init__(
        self,
        grid: Grid,
        rules: Iterable[Rule],
        position: GridCoord,
        direction: CardinalDirection,
        state: AntState,
    ):
        self._grid = grid
        self._position: GridCoord = position
        # The current direction of the ant (the last cardinal direction it stepped in)
        self._direction: CardinalDirection = direction
        self._state: AntState = state

        self._rules: dict[RuleKey, Rule] = {}
        for rule in rules:
            key = RuleKey(state=rule.state, colour=rule.colour)
            if key in self._rules:
                print(f"Warning: duplicate rules for {key}")
            self._rules[key] = rule

    @property
    def grid(self) -> Grid:
        return self._grid

    def step(self):
        # Look up the rule
        rule_key = RuleKey(state=self._state, colour=self._grid[self._position])
        rule = self._rules[rule_key]

        # change the ant's state and the colour of the cell the ant is on
        self._state = rule.new_state
        self._grid[self._position] = rule.new_colour

        # calculate the new direction, then move the ant in that direction
        self._direction = self._grid.get_direction(self._direction, rule.turn)
        self._position = self._grid.get_neighbour(self._position, self._direction)

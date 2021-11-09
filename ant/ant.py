from typing import Iterable, NamedTuple, NewType

from ant.grid import CardinalDirection, Colour, Coord, Grid

AntState = NewType("AntState", int)


class RuleKey(NamedTuple):
    state: AntState
    colour: Colour


class Rule(NamedTuple):
    state: AntState
    colour: Colour
    new_state: AntState
    new_colour: Colour
    turn: int


class Ant:
    def __init__(
        self,
        rules: Iterable[Rule],
        grid: Grid,
        position: Coord,
        direction: CardinalDirection,
        state: AntState,
    ):
        self._grid = grid
        self._position: Coord = position
        # The current direction of the ant (the last cardinal direction it stepped in)
        self._direction: CardinalDirection = direction
        self._state: AntState = state

        self._rules: dict[RuleKey, Rule] = {}
        for rule in rules:
            key = RuleKey(state=rule.state, colour=rule.colour)
            if key in self._rules:
                print(f"Warning: duplicate rules for {key}")
            self._rules[key] = rule

    def step(self):
        # Look up the rule
        colour = self._grid[self._position]
        rule = self._rules[RuleKey(state=self._state, colour=colour)]

        # change the ant's state and the colour of the cell the ant is on
        self._state = rule.new_state
        self._grid[self._position] = rule.new_colour

        # calculate the new direction, then move the ant in that direction
        self._direction = self._grid.get_direction(self._direction, rule.turn)
        self._position = self._grid.get_neighbour(self._position, self._direction)

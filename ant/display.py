from graphics import GraphWin, Point, Polygon

from ant.grid import Grid, GridCoord, HexGrid
from ant.types import Colour

COLOURS = [
    "black",
    "white",
    "red",
    "green",
    "blue",
    "yellow",
    "grey",
    "orange",
    "purple",
]


class Display:
    def __init__(self, grid: Grid, window_x: int = 1024, window_y: int = 1024):
        self._data_grid = grid
        self._display_grid: dict[GridCoord, Polygon] = {}
        self._window_x = window_x
        self._window_y = window_y
        self._window = GraphWin("ANT", window_x, window_y, autoflush=False)
        self._prev_bbox = (0, 0, 0, 0)

    def set_title(self, title: str) -> None:
        self._window.master.title(str(title))

    def render(self):
        bbox = self._data_grid.get_display_bbox()

        min_x, min_y, max_x, max_y = bbox

        x_scale = self._window_x / (max_x - min_x)
        y_scale = self._window_y / (max_y - min_y)

        scale = min(x_scale, y_scale)

        # TODO: Centre the image

        # If bbox changes, need a full redraw
        if bbox != self._prev_bbox:
            for item in self._window.items[:]:
                item.undraw()
            self._display_grid = {}
            self._prev_bbox = bbox

        for grid_coord, colour in self._data_grid:
            display_colour = COLOURS[colour % len(COLOURS)]

            if grid_coord in self._display_grid:
                # Change colour if necessary
                polygon = self._display_grid[grid_coord]
                if polygon.config["fill"] != display_colour:
                    polygon.setFill(display_colour)
            else:
                coords = []
                for display_coord in self._data_grid.get_cell_vertices(grid_coord):
                    x = (display_coord.x - min_x) * scale
                    y = (display_coord.y - min_y) * scale
                    coords.append(Point(x, y))

                polygon = Polygon(*coords)
                polygon.setFill(display_colour)

                self._display_grid[grid_coord] = polygon
                polygon.draw(self._window)

        self._window.update()


def test():
    grid = HexGrid(store_default=True)
    grid[GridCoord(-1, -1)] = Colour(0)
    grid[GridCoord(0, -1)] = Colour(1)
    grid[GridCoord(-1, 0)] = Colour(1)
    grid[GridCoord(0, 0)] = Colour(1)
    grid[GridCoord(0, 1)] = Colour(2)
    grid[GridCoord(1, 0)] = Colour(3)
    grid[GridCoord(1, 1)] = Colour(4)

    d = Display(grid)
    d.render()

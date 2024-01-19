from io import BytesIO

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
    def __init__(
        self,
        grid: Grid,
        window_x: int = 1024,
        window_y: int = 1024,
        show_cell_borders=False,
    ):
        self._data_grid = grid
        self._display_grid: dict[GridCoord, Polygon] = {}
        self._window_x = window_x
        self._window_y = window_y
        self._show_cell_borders = show_cell_borders
        self._window = GraphWin("ANT", window_x, window_y, autoflush=False)
        self._window.setBackground(COLOURS[0])
        self._prev_bbox = (0, 0, 0, 0)

    def set_title(self, title: str) -> None:
        self._window.master.title(str(title))

    def render(self):
        bbox = self._data_grid.get_display_bbox()

        min_x, min_y, max_x, max_y = bbox

        x_size = max_x - min_x
        y_size = max_y - min_y

        x_scale = self._window_x / x_size
        y_scale = self._window_y / y_size

        x_offset = min_x
        y_offset = min_y

        # Centre the image
        if x_scale < y_scale:
            scale = x_scale
            y_offset -= (self._window_y / scale - y_size) // 2
        else:
            scale = y_scale
            x_offset -= (self._window_x / scale - x_size) // 2

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
                    x = (display_coord.x - x_offset) * scale
                    y = (display_coord.y - y_offset) * scale
                    coords.append(Point(x, y))

                polygon = Polygon(*coords)
                if not self._show_cell_borders:
                    polygon.setOutline("")
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

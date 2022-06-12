from graphics import GraphWin, Point, Polygon

from ant.grid import Colour, Grid, GridCoord, HexGrid

COLOURS = {
    0: "black",
    1: "red",
    2: "green",
    3: "blue",
    4: "yellow",
}


class Display:
    def __init__(self, grid: Grid, window_x: int = 1024, window_y: int = 1024):
        self._grid = grid
        self._window_x = window_x
        self._window_y = window_y
        self._window = GraphWin("ANT", window_x, window_y)
        self._prev_bbox = (0, 0, 0, 0)

    def render(self):
        # TODO: Only redraw changed parts
        bbox = self._grid.get_display_bbox()

        min_x, min_y, max_x, max_y = bbox

        x_scale = self._window_x / (max_x - min_x)
        y_scale = self._window_y / (max_y - min_y)

        scale = min(x_scale, y_scale)

        if bbox != self._prev_bbox:
            for item in self._window.items[:]:
                item.undraw()
            self._prev_bbox = bbox

        for grid_coord, colour in self._grid:
            coords = []
            for display_coord in self._grid.get_cell_vertices(grid_coord):
                x = (display_coord.x - min_x) * scale
                y = (display_coord.y - min_y) * scale
                coords.append(Point(x, y))

            p = Polygon(*coords)
            p.setFill(COLOURS[colour])
            p.draw(self._window)


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

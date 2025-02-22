import abc
import math

from graphics import Circle, GraphicsObject, GraphWin, Line, Point, Polygon

from ant.grid import DisplayBBox, DisplayCoord, Grid, GridCoord, HexGrid, TriangleGrid
from ant.types import CellColour

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


class Display(abc.ABC):
    def __init__(
        self,
        grid: Grid,
        width_px: int,
        height_px: int,
        show_cell_borders: bool,
        show_ants: bool,
    ) -> None:
        self._data_grid = grid
        self._width_px = width_px
        self._height_px = height_px
        self._show_cell_borders = show_cell_borders
        self._show_ants = show_ants

    @abc.abstractmethod
    def render(self) -> None:
        pass


class WindowDisplay(Display):
    def __init__(
        self,
        grid: Grid,
        width_px: int = 1024,
        height_px: int = 1024,
        show_cell_borders: bool = False,
        show_ants: bool = True,
    ) -> None:
        super().__init__(
            grid=grid,
            width_px=width_px,
            height_px=height_px,
            show_cell_borders=show_cell_borders,
            show_ants=show_ants,
        )

        self._display_grid: dict[GridCoord, Polygon] = {}
        self._window = GraphWin("ANT", self._width_px, self._height_px, autoflush=False)
        self._window.setBackground(COLOURS[0])
        self._prev_bbox = DisplayBBox(DisplayCoord(0, 0), DisplayCoord(0, 0))

        self._display_ants: list[GraphicsObject] = []

    def set_title(self, title: str) -> None:
        self._window.master.title(str(title))  # type: ignore[attr-defined]

    def render(self) -> None:
        bbox = self._data_grid.get_display_bbox()

        x_size = bbox.max.x - bbox.min.x
        y_size = bbox.max.y - bbox.min.y

        x_scale = self._width_px / x_size
        y_scale = self._height_px / y_size

        x_offset = bbox.min.x
        y_offset = bbox.min.y

        # Centre the image
        if x_scale < y_scale:
            scale = x_scale
            y_offset -= (self._height_px / scale - y_size) // 2
        else:
            scale = y_scale
            x_offset -= (self._width_px / scale - x_size) // 2

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

        if self._show_ants:
            for ant_shape in self._display_ants:
                ant_shape.undraw()

            self._display_ants = []

            for i, ant in enumerate(self._data_grid.ants):
                # print(
                #     f"Ant {i}: x={ant.prev_position.x}, y={ant.prev_position.y}, direction={ant.state.direction.name}"
                # )
                ant_display_coord = self._data_grid.get_cell_centrepoint(
                    ant.prev_position
                )
                ant_x = (ant_display_coord.x - x_offset) * scale
                ant_y = (ant_display_coord.y - y_offset) * scale
                radius = 0.4 * scale
                ant_shape = Circle(Point(ant_x, ant_y), radius=radius)
                ant_shape.setFill("pink")
                ant_shape.setOutline("black")
                ant_shape.draw(self._window)

                angle = (
                    (180 - self._data_grid.get_ant_angle(ant.state.direction))
                    * math.pi
                    / 180
                )
                dx = radius * math.sin(angle)
                dy = radius * math.cos(angle)

                ant_arrow = Line(Point(ant_x, ant_y), Point(ant_x + dx, ant_y + dy))
                ant_arrow.draw(self._window)

                self._display_ants.extend([ant_shape, ant_arrow])

        self._window.update()


def test() -> None:
    grid = HexGrid(store_default=True)
    grid[GridCoord(-1, -1)] = CellColour(0)
    grid[GridCoord(0, -1)] = CellColour(1)
    grid[GridCoord(-1, 0)] = CellColour(1)
    grid[GridCoord(0, 0)] = CellColour(1)
    grid[GridCoord(0, 1)] = CellColour(2)
    grid[GridCoord(1, 0)] = CellColour(3)
    grid[GridCoord(1, 1)] = CellColour(4)

    # d = WindowDisplay(grid)
    # d.render()

    tg = TriangleGrid(store_default=True)
    tg[GridCoord(0, 0)] = CellColour(1)
    tg[GridCoord(2, 2)] = CellColour(2)
    d = WindowDisplay(tg)
    d.render()

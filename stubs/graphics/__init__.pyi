import tkinter as tk
from typing import Any, Callable, Literal, Self, overload

__version__: str

type FontFace = Literal["helvetica", "arial", "courier", "times roman"]
type FontStyle = Literal["bold", "normal", "italic", "bold italic"]
type Font = tuple[FontFace, float, FontStyle]

class GraphicsError(Exception): ...

OBJ_ALREADY_DRAWN: str
UNSUPPORTED_METHOD: str
BAD_OPTION: str

def update(rate: float | None = None) -> None: ...

class GraphWin(tk.Canvas):
    foreground: str
    items: list[GraphicsObject]
    mouseX: int | None
    mouseY: int | None
    height: int
    width: int
    autoflush: bool
    trans: Transform | None
    closed: bool
    lastKey: str
    def __init__(
        self,
        title: str = "Graphics Window",
        width: int = 200,
        height: int = 200,
        autoflush: bool = True,
    ) -> None: ...
    def setBackground(self, color: str) -> None: ...
    def setCoords(self, x1: int, y1: int, x2: int, y2: int) -> None: ...
    def close(self) -> None: ...
    def isClosed(self) -> bool: ...
    def isOpen(self) -> bool: ...
    def plot(self, x: int, y: int, color: str = "black") -> None: ...
    def plotPixel(self, x: int, y: int, color: str = "black") -> None: ...
    def flush(self) -> None: ...
    def getMouse(self) -> Point: ...
    def checkMouse(self) -> Point | None: ...
    def getKey(self) -> str: ...
    def checkKey(self) -> str: ...
    def getHeight(self) -> int: ...
    def getWidth(self) -> int: ...
    def toScreen(self, x: int, y: int) -> tuple[int, int]: ...
    def toWorld(self, x: int, y: int) -> tuple[int, int]: ...
    def setMouseHandler(self, func: Callable[[Point], None]) -> None: ...
    def addItem(self, item: GraphicsObject) -> None: ...
    def delItem(self, item: GraphicsObject) -> None: ...
    def redraw(self) -> None: ...

class Transform:
    xbase: int
    ybase: int
    xscale: float
    yscale: float
    def __init__(
        self, w: int, h: int, xlow: int, ylow: int, xhigh: int, yhigh: int
    ) -> None: ...
    def screen(self, x: int, y: int) -> tuple[int, int]: ...
    def world(self, xs: float, ys: float) -> tuple[float, float]: ...

DEFAULT_CONFIG: dict[str, Any]

class GraphicsObject:
    canvas: GraphWin | None
    id: int
    config: dict[str, Any]
    def __init__(self, options: dict[str, Any]) -> None: ...
    def setFill(self, color: str) -> None: ...
    def setOutline(self, color: str) -> None: ...
    def setWidth(self, width: float) -> None: ...
    def draw(self, graphwin: GraphWin) -> Self: ...
    def undraw(self) -> None: ...
    def move(self, dx: float, dy: float) -> None: ...

class Point(GraphicsObject):
    x: float
    y: float
    def __init__(self, x: float, y: float) -> None: ...
    def clone(self) -> Point: ...
    def getX(self) -> float: ...
    def getY(self) -> float: ...

class _BBox(GraphicsObject):
    p1: Point
    p2: Point
    def __init__(
        self, p1: Point, p2: Point, options: list[str] = ["outline", "width", "fill"]
    ) -> None: ...
    def getP1(self) -> Point: ...
    def getP2(self) -> Point: ...
    def getCenter(self) -> Point: ...

class Rectangle(_BBox):
    def __init__(self, p1: Point, p2: Point) -> None: ...
    def clone(self) -> Rectangle: ...

class Oval(_BBox):
    def __init__(self, p1: Point, p2: Point) -> None: ...
    def clone(self) -> Oval: ...

class Circle(Oval):
    radius: float
    def __init__(self, center: Point, radius: float) -> None: ...
    def clone(self) -> Circle: ...
    def getRadius(self) -> float: ...

class Line(_BBox):
    def __init__(self, p1: Point, p2: Point) -> None: ...
    def clone(self) -> Line: ...
    def setArrow(self, option: Literal["first", "last", "both", "none"]) -> None: ...

class Polygon(GraphicsObject):
    points: list[Point]
    def __init__(self, *points: Point) -> None: ...
    def clone(self) -> Polygon: ...
    def getPoints(self) -> list[Point]: ...

class Text(GraphicsObject):
    anchor: Point
    def __init__(self, p: Point, text: str) -> None: ...
    def clone(self) -> Text: ...
    def setText(self, text: str) -> None: ...
    def getText(self) -> str: ...
    def getAnchor(self) -> Point: ...
    def setFace(self, face: FontFace) -> None: ...
    def setSize(self, size: float) -> None: ...
    def setStyle(self, style: FontStyle) -> None: ...
    def setTextColor(self, color: str) -> None: ...

class Entry(GraphicsObject):
    anchor: Point
    width: float
    text: str
    fill: str
    color: str
    font: Font
    entry: tk.Entry
    def __init__(self, p: Point, width: float) -> None: ...
    def getText(self) -> str: ...
    def getAnchor(self) -> Point: ...
    def clone(self) -> Entry: ...
    def setText(self, t: str) -> None: ...
    def setFill(self, color: str) -> None: ...
    def setFace(self, face: FontFace) -> None: ...
    def setSize(self, size: float) -> None: ...
    def setStyle(self, style: FontStyle) -> None: ...
    def setTextColor(self, color: str) -> None: ...

class Image(GraphicsObject):
    idCount: int
    imageCache: dict[int, tk.PhotoImage]
    anchor: Point
    imageId: int
    img: tk.PhotoImage
    @overload
    def __init__(self, p: Point, filename: str) -> None: ...
    @overload
    def __init__(self, p: Point, width: int, height: int) -> None: ...
    def undraw(self) -> None: ...
    def getAnchor(self) -> Point: ...
    def clone(self) -> Image: ...
    def getWidth(self) -> float: ...
    def getHeight(self) -> float: ...
    def getPixel(self, x: int, y: int) -> list[int]: ...
    def setPixel(self, x: int, y: int, color: str) -> None: ...
    def save(self, filename: str) -> None: ...

def color_rgb(r: int, g: int, b: int) -> str: ...
def test() -> None: ...

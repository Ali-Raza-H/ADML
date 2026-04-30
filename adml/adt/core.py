from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class CanvasType(Enum):
    PRESENTATION = "presentation"
    DOCUMENT = "document"
    VECTOR = "vector"
    POSTER = "poster"
    SOCIAL = "social"

class PositionType(Enum):
    ABSOLUTE = "absolute"
    SEMANTIC = "semantic"
    FLOW = "flow"

class FillType(Enum):
    SOLID = "solid"
    GRADIENT = "gradient"
    IMAGE = "image"
    NONE = "none"

@dataclass
class Dimensions:
    width: float
    height: float
    unit: str = "pt"

@dataclass
class Colour:
    r: int
    g: int
    b: int
    a: float = 1.0

    @classmethod
    def from_hex(cls, hex_str: str) -> 'Colour':
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 3:
            hex_str = ''.join(c + c for c in hex_str)
        if len(hex_str) == 4:
            hex_str = ''.join(c + c for c in hex_str)
            
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        a = 1.0
        if len(hex_str) == 8:
            a = int(hex_str[6:8], 16) / 255.0
        return cls(r, g, b, a)

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, a: float = 1.0) -> 'Colour':
        return cls(r, g, b, a)

    def to_hex(self) -> str:
        if self.a < 1.0:
            return f"#{self.r:02x}{self.g:02x}{self.b:02x}{int(self.a * 255):02x}"
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_rgb_tuple(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def to_pptx_colour(self):
        from pptx.dml.color import RGBColor
        return RGBColor(self.r, self.g, self.b)

@dataclass
class Position:
    type: PositionType = PositionType.SEMANTIC
    semantic: str = "center"
    x: float = 0.0
    y: float = 0.0
    margin: float = 0.0
    offset_x: float = 0.0
    offset_y: float = 0.0

@dataclass
class FontSpec:
    family: str = "Arial"
    size: float = 24.0
    weight: str = "regular"
    style: str = "normal"
    colour: Colour = field(default_factory=lambda: Colour(0, 0, 0))
    line_height: float = 1.4
    letter_spacing: float = 0.0
    align: str = "left"

@dataclass
class Fill:
    type: FillType = FillType.SOLID
    colour: Colour | None = None
    start_colour: Colour | None = None
    end_colour: Colour | None = None
    direction: str = "vertical"
    image_src: str | None = None

@dataclass
class Shadow:
    x: float = 4.0
    y: float = 4.0
    blur: float = 12.0
    colour: Colour = field(default_factory=lambda: Colour(0, 0, 0, 0.3))

@dataclass
class Animation:
    type: str = "none"
    duration: float = 0.5
    delay: float = 0.0
    direction: str = "none"

@dataclass
class Element:
    id: str | None = None
    position: Position = field(default_factory=Position)
    width: float | None = None
    height: float | None = None
    opacity: float = 1.0
    shadow: Shadow | None = None
    animation: Animation | None = None

@dataclass
class TextElement(Element):
    content: str = ""
    font: FontSpec = field(default_factory=FontSpec)
    max_width: float | None = None
    overflow: str = "wrap"

@dataclass
class ShapeElement(Element):
    shape_type: str = "rectangle"
    fill: Fill = field(default_factory=Fill)
    stroke_colour: Colour | None = None
    stroke_width: float = 0.0
    corner_radius: float = 0.0

@dataclass
class ImageElement(Element):
    src: str = ""
    fit: str = "contain"
    alt: str = ""

@dataclass
class ListElement(Element):
    list_type: str = "bullet"
    items: list[str] = field(default_factory=list)
    font: FontSpec = field(default_factory=FontSpec)
    item_spacing: float = 12.0

@dataclass
class Slide:
    id: str
    background: Fill = field(default_factory=Fill)
    elements: list[Element] = field(default_factory=list)
    notes: str = ""
    width: float = 0.0
    height: float = 0.0

@dataclass
class DesignDocument:
    version: str = "1.0"
    canvas_type: CanvasType = CanvasType.PRESENTATION
    width: float = 1920.0
    height: float = 1080.0
    variables: dict[str, str] = field(default_factory=dict)
    slides: list[Slide] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

from abc import ABC, abstractmethod
from adml.adt.core import DesignDocument, Element, PositionType, Fill, FillType, Colour

class BaseRenderer(ABC):
    def __init__(self, doc: DesignDocument):
        self.doc = doc

    @abstractmethod
    def render(self) -> bytes:
        """Render document to bytes in target format."""
        ...

    @abstractmethod
    def get_file_extension(self) -> str:
        """Return the file extension for this format e.g. 'pptx'"""
        ...

    def resolve_position(
        self,
        element: Element,
        canvas_w: float,
        canvas_h: float
    ) -> tuple[float, float]:
        pos = element.position
        if pos.type == PositionType.FLOW:
            return (0.0, 0.0)
        if pos.type == PositionType.ABSOLUTE:
            return (pos.x, pos.y)

        el_w = element.width or 0.0
        el_h = element.height or 0.0
        margin = pos.margin
        sem = pos.semantic

        x = pos.offset_x
        y = pos.offset_y

        if sem == "center":
            x += (canvas_w - el_w) / 2
            y += (canvas_h - el_h) / 2
        elif sem == "center-top":
            x += (canvas_w - el_w) / 2
            y += margin + pos.offset_y
        elif sem == "center-bottom":
            x += (canvas_w - el_w) / 2
            y += canvas_h - el_h - margin + pos.offset_y
        elif sem == "center-left":
            x += margin + pos.offset_x
            y += (canvas_h - el_h) / 2
        elif sem == "center-right":
            x += canvas_w - el_w - margin + pos.offset_x
            y += (canvas_h - el_h) / 2
        elif sem == "top-left":
            x += margin + pos.offset_x
            y += margin + pos.offset_y
        elif sem == "top-right":
            x += canvas_w - el_w - margin + pos.offset_x
            y += margin + pos.offset_y
        elif sem == "bottom-left":
            x += margin + pos.offset_x
            y += canvas_h - el_h - margin + pos.offset_y
        elif sem == "bottom-right":
            x += canvas_w - el_w - margin + pos.offset_x
            y += canvas_h - el_h - margin + pos.offset_y
        
        return (x, y)

    def resolve_background_colour(self, fill: Fill) -> Colour:
        if fill.type == FillType.SOLID and fill.colour:
            return fill.colour
        if fill.type == FillType.GRADIENT and fill.start_colour:
            return fill.start_colour
        return Colour(255, 255, 255)

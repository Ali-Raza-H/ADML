from adml.adt.core import Colour, Position, PositionType, TextElement
from adml.utils.colours import contrast_ratio, is_readable, parse_colour
from adml.utils.units import to_points
from adml.renderers.base import BaseRenderer

def test_colour_from_hex():
    c = Colour.from_hex("#ff0000")
    assert c.r == 255
    assert c.g == 0
    assert c.b == 0
    assert c.a == 1.0

def test_colour_to_hex():
    c = Colour(255, 0, 0)
    assert c.to_hex() == "#ff0000"
    c2 = Colour(255, 0, 0, 0.5)
    assert c2.to_hex() == "#ff00007f"

def test_contrast_ratio():
    black = Colour(0, 0, 0)
    white = Colour(255, 255, 255)
    assert round(contrast_ratio(black, white), 1) == 21.0
    assert round(contrast_ratio(black, black), 1) == 1.0

def test_is_readable():
    black = Colour(0, 0, 0)
    white = Colour(255, 255, 255)
    assert is_readable(black, white) == True
    assert is_readable(black, black) == False

def test_resolve_position():
    class DummyRenderer(BaseRenderer):
        def render(self): pass
        def get_file_extension(self): return "dummy"

    renderer = DummyRenderer(None)
    el = TextElement()
    el.width = 100
    el.height = 50
    el.position = Position(type=PositionType.SEMANTIC, semantic="center")
    
    x, y = renderer.resolve_position(el, 800, 600)
    assert x == 350
    assert y == 275

def test_unit_conversions():
    assert to_points(96, "px") == 72.0
    assert abs(to_points(25.4, "mm") - 72.0) < 0.1

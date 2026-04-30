import re
from adml.adt.core import Colour

NAMED_COLOURS = {
    "white": Colour(255, 255, 255),
    "black": Colour(0, 0, 0),
    "red": Colour(255, 0, 0),
    "blue": Colour(0, 0, 255),
    "green": Colour(0, 255, 0),
    "transparent": Colour(0, 0, 0, 0.0),
}

def parse_colour(value: str) -> Colour | None:
    value = value.strip().lower()
    if value.startswith("var("):
        return None  # To be resolved later
    if value in NAMED_COLOURS:
        return NAMED_COLOURS[value]
    if value.startswith("#"):
        return hex_to_colour(value)
    
    rgb_match = re.match(r"rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([0-9.]+)\s*)?\)", value)
    if rgb_match:
        r, g, b, a = rgb_match.groups()
        return Colour(int(r), int(g), int(b), float(a) if a is not None else 1.0)
    
    return None

def hex_to_colour(hex_str: str) -> Colour:
    return Colour.from_hex(hex_str)

def colour_to_hex(c: Colour) -> str:
    return c.to_hex()

def colour_to_pptx(c: Colour):
    return c.to_pptx_colour()

def _luminance(c: Colour) -> float:
    def _c_srgb(val: float) -> float:
        val /= 255.0
        return val / 12.92 if val <= 0.03928 else ((val + 0.055) / 1.055) ** 2.4
    return 0.2126 * _c_srgb(c.r) + 0.7152 * _c_srgb(c.g) + 0.0722 * _c_srgb(c.b)

def contrast_ratio(c1: Colour, c2: Colour) -> float:
    l1 = _luminance(c1)
    l2 = _luminance(c2)
    bright = max(l1, l2)
    dark = min(l1, l2)
    return (bright + 0.05) / (dark + 0.05)

def is_readable(text_colour: Colour, bg_colour: Colour, large_text: bool = False) -> bool:
    ratio = contrast_ratio(text_colour, bg_colour)
    target = 3.0 if large_text else 4.5
    return ratio >= target

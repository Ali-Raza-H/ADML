import platform
from adml.adt.core import FontSpec

FONT_WEIGHT_MAP = {
    "thin": 100, "extralight": 200, "light": 300,
    "regular": 400, "normal": 400, "medium": 500,
    "semibold": 600, "bold": 700, "extrabold": 800, "black": 900
}

SYSTEM_FONT_FALLBACKS = {
    "Inter": ["Segoe UI", "Arial", "Helvetica", "sans-serif"],
    "default": ["Arial", "Helvetica", "sans-serif"],
}

def resolve_font_family(requested: str) -> str:
    return requested

def get_available_fonts() -> list[str]:
    return ["Arial", "Helvetica", "Times New Roman", "Courier New"]

def parse_font_shorthand(shorthand: str) -> FontSpec:
    import re
    family_match = re.search(r'"([^"]+)"', shorthand)
    family = family_match.group(1) if family_match else "Arial"
    
    remainder = shorthand.replace(f'"{family}"', '').strip()
    parts = remainder.split()
    
    spec = FontSpec(family=family)
    for part in parts:
        part_lower = part.lower()
        if part_lower in FONT_WEIGHT_MAP:
            spec.weight = part_lower
        elif part_lower in ["italic", "normal"]:
            spec.style = part_lower
        elif "px" in part_lower or "pt" in part_lower:
            from adml.utils.units import parse_dimension, to_points
            val, unit = parse_dimension(part_lower)
            spec.size = to_points(val, unit)
        else:
            try:
                spec.size = float(part)
            except ValueError:
                pass
                
    return spec

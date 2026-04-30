import re
from adml.adt.core import (
    DesignDocument, Slide, Element, Position, PositionType, Fill, FillType
)
from adml.utils.colours import parse_colour
from adml.utils.fonts import parse_font_shorthand
from adml.utils.units import parse_dimension, to_points

def _resolve_var(value: str, variables: dict[str, str]) -> str:
    if not isinstance(value, str):
        return value
    
    def replace_var(match):
        var_name = match.group(1)
        return variables.get(var_name, match.group(0))
        
    resolved = re.sub(r'var\(--([a-zA-Z_][a-zA-Z0-9_-]*)\)', replace_var, value)
    return resolved

def _resolve_position(pos_str: str) -> Position:
    pos = Position()
    pos_str = pos_str.strip()
    
    match = re.match(r'([a-zA-Z-]+)(?:\((.*)\))?', pos_str)
    if not match:
        pos.semantic = pos_str
        return pos
        
    semantic, args_str = match.groups()
    pos.semantic = semantic
    
    if semantic in ("absolute", "flow"):
        pos.type = PositionType.ABSOLUTE if semantic == "absolute" else PositionType.FLOW
    else:
        pos.type = PositionType.SEMANTIC
        
    if args_str:
        args = [arg.strip() for arg in args_str.split(',')]
        for arg in args:
            if '=' in arg:
                k, v = arg.split('=', 1)
                k = k.strip()
                v = v.strip()
                val, unit = parse_dimension(v)
                pts = to_points(val, unit)
                if k == 'margin':
                    pos.margin = pts
                elif k == 'offset':
                    pos.offset_y = pts # default offset to y
                elif k == 'offset-x':
                    pos.offset_x = pts
                elif k == 'offset-y':
                    pos.offset_y = pts
                elif k == 'x':
                    pos.x = pts
                elif k == 'y':
                    pos.y = pts
    return pos

def resolve(doc: DesignDocument) -> DesignDocument:
    variables = doc.variables
    
    for slide in doc.slides:
        slide.width = doc.width
        slide.height = doc.height
        
        # Resolve slide background
        if hasattr(slide, '_raw_props'):
            bg_val = slide._raw_props.get('background')
            if bg_val:
                bg_val = _resolve_var(bg_val, variables)
                if bg_val.startswith("gradient"):
                    slide.background.type = FillType.GRADIENT
                    matches = re.findall(r'(#[a-fA-F0-9]+|rgba?\([^)]+\)|[a-zA-Z]+)', bg_val)
                    if len(matches) >= 2:
                        slide.background.start_colour = parse_colour(matches[0])
                        slide.background.end_colour = parse_colour(matches[1])
                else:
                    slide.background.type = FillType.SOLID
                    slide.background.colour = parse_colour(bg_val)
        
        for el in slide.elements:
            raw_props = getattr(el, '_raw_props', {})
            
            for k, v in raw_props.items():
                v = _resolve_var(v, variables)
                if k == 'position':
                    el.position = _resolve_position(v)
                elif k == 'color' and hasattr(el, 'font'):
                    el.font.colour = parse_colour(v)
                elif k == 'font' and hasattr(el, 'font'):
                    font_spec = parse_font_shorthand(v)
                    el.font.family = font_spec.family
                    if font_spec.weight != "regular":
                        el.font.weight = font_spec.weight
                    if font_spec.style != "normal":
                        el.font.style = font_spec.style
                    if font_spec.size != 24.0:
                        el.font.size = font_spec.size
                elif k == 'fill' and hasattr(el, 'fill'):
                    if v.startswith("gradient"):
                        el.fill.type = FillType.GRADIENT
                        matches = re.findall(r'(#[a-fA-F0-9]+|rgba?\([^)]+\)|[a-zA-Z]+)', v)
                        if len(matches) >= 2:
                            el.fill.start_colour = parse_colour(matches[0])
                            el.fill.end_colour = parse_colour(matches[1])
                    else:
                        el.fill.type = FillType.SOLID
                        el.fill.colour = parse_colour(v)
                        
    return doc

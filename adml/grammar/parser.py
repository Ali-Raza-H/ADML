import json
from pathlib import Path
from lark import Lark, Transformer, v_args
from lark.exceptions import UnexpectedInput, UnexpectedCharacters

from adml.adt.core import (
    DesignDocument, Slide, TextElement, ShapeElement, ListElement, ImageElement,
    Fill, Position, FontSpec, Colour, Dimensions, CanvasType, PositionType, FillType
)
from adml.utils.units import parse_dimension, to_points

class ADMLSyntaxError(Exception):
    def __init__(self, message, line, column):
        super().__init__(f"Syntax Error at line {line}, column {column}:\n{message}")
        self.line = line
        self.column = column

@v_args(inline=True)
class ADMLTransformer(Transformer):
    def __init__(self):
        self.variables = {}
        
    def start(self, *args):
        doc = DesignDocument()
        for arg in args:
            if isinstance(arg, tuple) and arg[0] == "version":
                doc.version = arg[1]
            elif isinstance(arg, tuple) and arg[0] == "canvas":
                doc.canvas_type = arg[1].get("type", CanvasType.PRESENTATION)
                doc.width = arg[1].get("width", 1920.0)
                doc.height = arg[1].get("height", 1080.0)
            elif isinstance(arg, tuple) and arg[0] == "vars":
                doc.variables.update(arg[1])
            elif isinstance(arg, Slide):
                doc.slides.append(arg)
        doc.variables = self.variables
        return doc

    def version_decl(self, number):
        return ("version", str(number))

    def canvas_decl(self, props):
        canvas_props = {}
        if props:
            for k, v in props:
                if k == "type":
                    try:
                        canvas_props["type"] = CanvasType(v.upper())
                    except ValueError:
                        pass
                elif k in ("width", "height"):
                    val, unit = parse_dimension(str(v))
                    canvas_props[k] = to_points(val, unit)
        return ("canvas", canvas_props)

    def decl_properties(self, *props):
        return props

    def decl_property(self, key, value_list):
        return (str(key), value_list[0])

    def vars_block(self, *vars):
        return ("vars", dict(vars))

    def var_property(self, key, value_list):
        self.variables[str(key)] = str(value_list[0])
        return (str(key), str(value_list[0]))

    def slide(self, name, *items):
        name = str(name).strip('"')
        slide = Slide(id=name)
        slide._raw_props = {}
        for item in items:
            if isinstance(item, tuple) and item[0] == "property":
                k, v = item[1], item[2]
                slide._raw_props[k] = v
                if k == "background":
                    fill = Fill()
                    slide.background = fill
            else:
                slide.elements.append(item)
        return slide

    def property(self, key, value_list):
        if len(value_list) == 1:
            return ("property", str(key), value_list[0])
        return ("property", str(key), " ".join(str(x) for x in value_list))

    def value_list(self, *values):
        return list(values)

    def text_element(self, content, *props):
        content = str(content).strip('"')
        el = TextElement(content=content)
        self._apply_props(el, props)
        return el

    def shape_element(self, shape_type, *props):
        el = ShapeElement(shape_type=str(shape_type))
        self._apply_props(el, props)
        return el

    def list_element(self, list_type, *items_and_props):
        el = ListElement(list_type=str(list_type))
        for item in items_and_props:
            if isinstance(item, tuple) and item[0] == "property":
                self._apply_props(el, [item])
            elif isinstance(item, tuple) and item[0] == "item":
                el.items.append(item[1])
        return el

    def list_item(self, content):
        return ("item", str(content).strip('"'))

    def image_element(self, src, *props):
        src = str(src).strip('"')
        el = ImageElement(src=src)
        self._apply_props(el, props)
        return el

    def _apply_props(self, el, props):
        for prop in props:
            if not isinstance(prop, tuple) or prop[0] != "property":
                continue
            k, v = prop[1], prop[2]
            if k == "font":
                pass
            elif k == "size":
                if hasattr(el, 'font'):
                    val, unit = parse_dimension(str(v))
                    el.font.size = to_points(val, unit)
            elif k == "color":
                if hasattr(el, 'font'):
                    el.font.colour = None
            elif k == "position":
                pass
            elif k == "width":
                val, unit = parse_dimension(str(v))
                el.width = to_points(val, unit)
            elif k == "height":
                val, unit = parse_dimension(str(v))
                el.height = to_points(val, unit)
            elif k == "fill" and hasattr(el, 'fill'):
                el.fill.type = FillType.SOLID
            elif k == "corner-radius" and hasattr(el, 'corner_radius'):
                val, unit = parse_dimension(str(v))
                el.corner_radius = to_points(val, unit)
            if not hasattr(el, '_raw_props'):
                el._raw_props = {}
            el._raw_props[k] = v

    def dimension_val(self, val): return str(val)
    def number_val(self, val): return str(val)
    def color_val(self, val): return str(val)
    def gradient_val(self, val): return str(val)
    def string_val(self, val): return str(val)
    def var_val(self, val): return str(val)
    def ident_val(self, val): return str(val)
    def func_val(self, call_tuple):
        name, args = call_tuple
        return f"{name}({args})"
    def func_call(self, name, args): return str(name), str(args)
    def func_args(self, *args): return ",".join(str(a) for a in args)
    def func_arg(self, *args):
        if len(args) == 2:
            return f"{args[0]}={args[1]}"
        return str(args[0])

grammar_path = Path(__file__).parent / "adml.lark"
with open(grammar_path, "r", encoding="utf-8") as f:
    grammar_text = f.read()

parser = Lark(grammar_text, start="start", parser="earley")

def parse(source: str) -> DesignDocument:
    try:
        tree = parser.parse(source)
        transformer = ADMLTransformer()
        doc = transformer.transform(tree)
        return doc
    except UnexpectedCharacters as e:
        raise ADMLSyntaxError(str(e), e.line, e.column)
    except UnexpectedInput as e:
        raise ADMLSyntaxError(str(e), e.line, e.column)

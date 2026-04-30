from adml.adt.core import Slide, TextElement, ShapeElement, ListElement, Element, FillType, Fill, FontSpec
from adml.renderers.base import BaseRenderer

class HTMLRenderer(BaseRenderer):

    def get_file_extension(self) -> str:
        return "html"

    def render(self) -> bytes:
        slides_html = "\n".join(self._render_slide_html(s, i) for i, s in enumerate(self.doc.slides))
        
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>ADML Preview</title>
<style>
body {{
    margin: 0;
    padding: 0;
    background: #111;
    color: #fff;
    font-family: sans-serif;
    display: flex;
    flex-direction: column;
    height: 100vh;
}}
.toolbar {{
    padding: 10px 20px;
    background: #222;
    display: flex;
    align-items: center;
    gap: 15px;
}}
button {{
    background: #4f46e5;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}}
button:hover {{ background: #4338ca; }}
.slides-container {{
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: auto;
    padding: 20px;
}}
.slide {{
    display: none;
    position: relative;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    background: white;
    overflow: hidden;
}}
.slide.active {{
    display: block;
}}
</style>
</head>
<body>
<div class="toolbar">
    <button onclick="prev()">Prev</button>
    <span id="counter">1 / {len(self.doc.slides)}</span>
    <button onclick="next()">Next</button>
</div>
<div class="slides-container">
    {slides_html}
</div>
<script>
let current = 0;
const slides = document.querySelectorAll('.slide');
function show(idx) {{
    if(idx < 0) idx = 0;
    if(idx >= slides.length) idx = slides.length - 1;
    slides.forEach(s => s.classList.remove('active'));
    slides[idx].classList.add('active');
    document.getElementById('counter').innerText = (idx + 1) + ' / ' + slides.length;
    current = idx;
}}
function next() {{ show(current + 1); }}
function prev() {{ show(current - 1); }}
if(slides.length > 0) show(0);
</script>
</body>
</html>"""
        return html.encode('utf-8')

    def _render_slide_html(self, slide: Slide, index: int) -> str:
        w_px = slide.width * 1.333
        h_px = slide.height * 1.333
        bg_css = self._fill_to_css(slide.background)
        
        elements_html = []
        for el in slide.elements:
            if isinstance(el, TextElement):
                elements_html.append(self._render_text_html(el, slide))
            elif isinstance(el, ShapeElement):
                elements_html.append(self._render_shape_html(el, slide))
            elif isinstance(el, ListElement):
                elements_html.append(self._render_list_html(el, slide))
                
        els_str = "\n".join(elements_html)
        return f'<div class="slide" style="width: {w_px}px; height: {h_px}px; {bg_css}">\n{els_str}\n</div>'

    def _render_text_html(self, element: TextElement, slide: Slide) -> str:
        pos_css = self._position_to_css(element, slide)
        font_css = self._font_to_css(element.font)
        align_css = f"text-align: {element.font.align};"
        w_css = f"width: {element.width * 1.333}px;" if element.width else "white-space: pre-wrap;"
        content = element.content.replace("\n", "<br>")
        return f'<div style="{pos_css} {font_css} {align_css} {w_css}">{content}</div>'

    def _render_shape_html(self, element: ShapeElement, slide: Slide) -> str:
        pos_css = self._position_to_css(element, slide)
        bg_css = self._fill_to_css(element.fill)
        w_px = (element.width or 100.0) * 1.333
        h_px = (element.height or 100.0) * 1.333
        
        extra_css = ""
        if element.shape_type == "circle" or element.shape_type == "ellipse":
            extra_css += "border-radius: 50%;"
        elif element.shape_type == "rectangle" and element.corner_radius > 0:
            extra_css += f"border-radius: {element.corner_radius * 1.333}px;"
            
        if element.stroke_width > 0 and element.stroke_colour:
            extra_css += f"border: {element.stroke_width * 1.333}px solid rgba({element.stroke_colour.r},{element.stroke_colour.g},{element.stroke_colour.b},{element.stroke_colour.a});"
            
        return f'<div style="{pos_css} width: {w_px}px; height: {h_px}px; {bg_css} {extra_css}"></div>'

    def _render_list_html(self, element: ListElement, slide: Slide) -> str:
        pos_css = self._position_to_css(element, slide)
        font_css = self._font_to_css(element.font)
        
        tag = "ul" if element.list_type == "bullet" else "ol"
        items_html = "".join(f"<li style='margin-bottom: {element.item_spacing * 1.333}px'>{item}</li>" for item in element.items)
        return f'<{tag} style="{pos_css} {font_css} margin: 0; padding-left: 2em;">{items_html}</{tag}>'

    def _position_to_css(self, element: Element, slide: Slide) -> str:
        x, y = self.resolve_position(element, slide.width, slide.height)
        return f"position: absolute; left: {x * 1.333}px; top: {y * 1.333}px;"

    def _fill_to_css(self, fill: Fill) -> str:
        if fill.type == FillType.SOLID and fill.colour:
            return f"background-color: rgba({fill.colour.r},{fill.colour.g},{fill.colour.b},{fill.colour.a});"
        elif fill.type == FillType.GRADIENT and fill.start_colour and fill.end_colour:
            c1 = fill.start_colour
            c2 = fill.end_colour
            return f"background: linear-gradient(to bottom, rgba({c1.r},{c1.g},{c1.b},{c1.a}), rgba({c2.r},{c2.g},{c2.b},{c2.a}));"
        return "background-color: transparent;"

    def _font_to_css(self, font: FontSpec) -> str:
        c = font.colour
        c_str = f"rgba({c.r},{c.g},{c.b},{c.a})" if c else "inherit"
        return f"font-family: '{font.family}'; font-size: {font.size * 1.333}px; font-weight: {font.weight}; font-style: {font.style}; color: {c_str}; line-height: {font.line_height};"

from xml.etree.ElementTree import Element as XmlElement, SubElement, tostring
from adml.adt.core import Slide, TextElement, ShapeElement, ListElement, ImageElement, FillType, Colour
from adml.renderers.base import BaseRenderer

class SVGRenderer(BaseRenderer):

    def get_file_extension(self) -> str:
        return "svg"

    def render(self) -> bytes:
        total_height = self.doc.height * len(self.doc.slides) + (50 * max(0, len(self.doc.slides) - 1))
        width = self.doc.width
        
        svg = XmlElement('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'viewBox': f"0 0 {width} {total_height}",
            'width': f"{width}pt",
            'height': f"{total_height}pt"
        })
        
        defs = SubElement(svg, 'defs')
        self._defs = defs
        self._gradient_count = 0
        
        y_offset = 0.0
        for slide in self.doc.slides:
            group = SubElement(svg, 'g', {'transform': f'translate(0, {y_offset})'})
            self._render_slide_svg(group, slide)
            y_offset += self.doc.height + 50.0
            
        return tostring(svg, encoding='utf-8')

    def _get_gradient_id(self, fill) -> str:
        self._gradient_count += 1
        grad_id = f"grad_{self._gradient_count}"
        grad = SubElement(self._defs, 'linearGradient', {
            'id': grad_id,
            'x1': '0%', 'y1': '0%', 'x2': '0%', 'y2': '100%'
        })
        stop1 = SubElement(grad, 'stop', {'offset': '0%'})
        if fill.start_colour:
            stop1.set('stop-color', self._colour_to_svg(fill.start_colour))
        stop2 = SubElement(grad, 'stop', {'offset': '100%'})
        if fill.end_colour:
            stop2.set('stop-color', self._colour_to_svg(fill.end_colour))
        return grad_id

    def _render_slide_svg(self, parent_group, slide: Slide):
        self._render_background_svg(parent_group, slide)
        for el in slide.elements:
            if isinstance(el, TextElement):
                self._render_text_svg(parent_group, el, slide)
            elif isinstance(el, ShapeElement):
                self._render_shape_svg(parent_group, el, slide)
            elif isinstance(el, ListElement):
                self._render_list_svg(parent_group, el, slide)

    def _render_background_svg(self, group, slide: Slide):
        rect = SubElement(group, 'rect', {
            'x': '0', 'y': '0',
            'width': str(slide.width),
            'height': str(slide.height)
        })
        if slide.background.type == FillType.SOLID and slide.background.colour:
            rect.set('fill', self._colour_to_svg(slide.background.colour))
        elif slide.background.type == FillType.GRADIENT:
            grad_id = self._get_gradient_id(slide.background)
            rect.set('fill', f"url(#{grad_id})")
        else:
            rect.set('fill', 'white')

    def _render_text_svg(self, group, element: TextElement, slide: Slide):
        x_pt, y_pt = self.resolve_position(element, slide.width, slide.height)
        
        y_pt += element.font.size
        
        text_el = SubElement(group, 'text', {
            'x': str(x_pt), 'y': str(y_pt),
            'font-family': element.font.family,
            'font-size': str(element.font.size),
        })
        if element.font.colour:
            text_el.set('fill', self._colour_to_svg(element.font.colour))
        if element.font.weight != "regular":
            text_el.set('font-weight', element.font.weight)
        if element.font.style == "italic":
            text_el.set('font-style', "italic")
            
        anchor = "start"
        if element.font.align == "center":
            anchor = "middle"
            text_el.set('x', str(x_pt + (element.width or slide.width)/2))
        elif element.font.align == "right":
            anchor = "end"
            text_el.set('x', str(x_pt + (element.width or slide.width)))
        text_el.set('text-anchor', anchor)
        
        lines = element.content.split('\n')
        for i, line in enumerate(lines):
            if i == 0:
                text_el.text = line
            else:
                tspan = SubElement(text_el, 'tspan', {'x': text_el.get('x'), 'dy': "1.4em"})
                tspan.text = line

    def _render_shape_svg(self, group, element: ShapeElement, slide: Slide):
        x_pt, y_pt = self.resolve_position(element, slide.width, slide.height)
        w_pt = element.width or 100.0
        h_pt = element.height or 100.0
        
        shape_type = element.shape_type
        attrs = {}
        if shape_type == "rectangle":
            attrs = {'x': str(x_pt), 'y': str(y_pt), 'width': str(w_pt), 'height': str(h_pt)}
            if element.corner_radius > 0:
                attrs['rx'] = str(element.corner_radius)
            shape = SubElement(group, 'rect', attrs)
        elif shape_type == "circle":
            r = min(w_pt, h_pt) / 2
            attrs = {'cx': str(x_pt + r), 'cy': str(y_pt + r), 'r': str(r)}
            shape = SubElement(group, 'circle', attrs)
        elif shape_type == "ellipse":
            attrs = {'cx': str(x_pt + w_pt/2), 'cy': str(y_pt + h_pt/2), 'rx': str(w_pt/2), 'ry': str(h_pt/2)}
            shape = SubElement(group, 'ellipse', attrs)
        elif shape_type == "line":
            attrs = {'x1': str(x_pt), 'y1': str(y_pt), 'x2': str(x_pt + w_pt), 'y2': str(y_pt + h_pt)}
            shape = SubElement(group, 'line', attrs)
        else:
            return
            
        if element.fill.type == FillType.SOLID and element.fill.colour:
            shape.set('fill', self._colour_to_svg(element.fill.colour))
        elif element.fill.type == FillType.GRADIENT:
            grad_id = self._get_gradient_id(element.fill)
            shape.set('fill', f"url(#{grad_id})")
        else:
            shape.set('fill', 'none')
            
        if element.stroke_width > 0 and element.stroke_colour:
            shape.set('stroke', self._colour_to_svg(element.stroke_colour))
            shape.set('stroke-width', str(element.stroke_width))

    def _render_list_svg(self, group, element: ListElement, slide: Slide):
        x_pt, y_pt = self.resolve_position(element, slide.width, slide.height)
        y_pt += element.font.size
        
        for i, item in enumerate(element.items):
            text_el = SubElement(group, 'text', {
                'x': str(x_pt), 'y': str(y_pt),
                'font-family': element.font.family,
                'font-size': str(element.font.size),
            })
            if element.font.colour:
                text_el.set('fill', self._colour_to_svg(element.font.colour))
                
            prefix = "• " if element.list_type == "bullet" else f"{i+1}. "
            text_el.text = prefix + item
            y_pt += element.font.size * element.font.line_height + element.item_spacing

    def _colour_to_svg(self, colour: Colour) -> str:
        return f"rgba({colour.r},{colour.g},{colour.b},{colour.a})"

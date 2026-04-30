import pytest
from adml.grammar.parser import parse, ADMLSyntaxError
from adml.adt.core import CanvasType, FillType

def test_minimal_document():
    doc = parse('slide("test") { }')
    assert len(doc.slides) == 1
    assert doc.slides[0].id == "test"

def test_version_decl():
    doc = parse('@version(1.0)')
    assert doc.version == "1.0"

def test_canvas_decl():
    doc = parse('@canvas(type=document, width=800px, height=600px)')
    assert doc.canvas_type == CanvasType.DOCUMENT
    assert doc.width == 600.0
    assert doc.height == 450.0

def test_vars_block():
    doc = parse('@vars { --primary: #ff0000 --size: 24px }')
    assert doc.variables['--primary'] == '#ff0000'
    assert doc.variables['--size'] == '24px'

def test_slide_background():
    doc = parse('slide("test") { background: #ffffff }')
    assert len(doc.slides) == 1
    assert doc.slides[0]._raw_props['background'] == '#ffffff'

def test_text_element():
    doc = parse('slide("s") { text("hello") { font: "Inter" bold \n size: 24px } }')
    el = doc.slides[0].elements[0]
    assert el.content == "hello"
    assert el._raw_props['font'] == '"Inter" bold'
    assert el.font.size == 18.0

def test_shape_rectangle():
    doc = parse('slide("s") { shape(rectangle) { corner-radius: 4px } }')
    el = doc.slides[0].elements[0]
    assert el.shape_type == "rectangle"
    assert el.corner_radius == 3.0

def test_shape_circle():
    doc = parse('slide("s") { shape(circle) {} }')
    el = doc.slides[0].elements[0]
    assert el.shape_type == "circle"

def test_list_bullet():
    doc = parse('slide("s") { list(bullet) { item("one") item("two") } }')
    el = doc.slides[0].elements[0]
    assert el.list_type == "bullet"
    assert el.items == ["one", "two"]

def test_hex_colours():
    doc = parse('slide("s") { text("t") { color: #f00 \n color: #ff0000 \n color: #ff0000ff } }')
    el = doc.slides[0].elements[0]
    assert el._raw_props['color'] == '#ff0000ff'

def test_rgba_colours():
    doc = parse('slide("s") { text("t") { color: rgba(255, 0, 0, 0.5) } }')
    el = doc.slides[0].elements[0]
    assert el._raw_props['color'] == 'rgba(255, 0, 0, 0.5)'

def test_gradient_values():
    doc = parse('slide("s") { shape(rectangle) { fill: gradient(#f00 -> #00f) } }')
    el = doc.slides[0].elements[0]
    assert el._raw_props['fill'] == 'gradient(#f00 -> #00f)'

def test_position_center():
    doc = parse('slide("s") { text("t") { position: center } }')
    el = doc.slides[0].elements[0]
    assert el._raw_props['position'] == 'center'

def test_position_margin():
    doc = parse('slide("s") { text("t") { position: top-left(margin=20) } }')
    el = doc.slides[0].elements[0]
    assert el._raw_props['position'] == 'top-left(margin=20)'

def test_syntax_error():
    with pytest.raises(ADMLSyntaxError):
        parse('slide( { }')

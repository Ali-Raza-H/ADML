import os
from pathlib import Path
from adml.grammar.parser import parse
from adml.adt.resolver import resolve
from adml.renderers.pptx_renderer import PowerPointRenderer
from adml.renderers.svg_renderer import SVGRenderer
from adml.renderers.html_renderer import HTMLRenderer

def get_fixture(name):
    path = Path(__file__).parent / "fixtures" / name
    with open(path, "r", encoding="utf-8") as f:
        return resolve(parse(f.read()))

def test_pptx_renderer():
    doc = get_fixture("simple.adml")
    renderer = PowerPointRenderer(doc)
    out = renderer.render()
    assert len(out) > 0
    assert out.startswith(b"PK")

def test_svg_renderer():
    doc = get_fixture("simple.adml")
    renderer = SVGRenderer(doc)
    out = renderer.render()
    assert len(out) > 0
    assert out.decode('utf-8').startswith("<svg")

def test_html_renderer():
    doc = get_fixture("simple.adml")
    renderer = HTMLRenderer(doc)
    out = renderer.render()
    assert len(out) > 0
    assert out.decode('utf-8').startswith("<!DOCTYPE html>")

def test_empty_slide():
    doc = resolve(parse('slide("empty") {}'))
    assert len(PowerPointRenderer(doc).render()) > 0
    assert len(SVGRenderer(doc).render()) > 0
    assert len(HTMLRenderer(doc).render()) > 0

def test_two_slides_pptx():
    doc = get_fixture("two_slides.adml")
    assert len(PowerPointRenderer(doc).render()) > 0

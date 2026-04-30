from adml.renderers.pptx_renderer import PowerPointRenderer
from adml.renderers.svg_renderer import SVGRenderer
from adml.renderers.html_renderer import HTMLRenderer

RENDERERS = {
    "pptx": PowerPointRenderer,
    "svg":  SVGRenderer,
    "ai":   SVGRenderer,
    "html": HTMLRenderer,
}

def render(doc, format: str) -> bytes:
    cls = RENDERERS.get(format.lower())
    if not cls:
        raise ValueError(
            f"Unknown format '{format}'. "
            f"Available: {', '.join(RENDERERS.keys())}"
        )
    return cls(doc).render()

def available_formats() -> list[str]:
    return list(RENDERERS.keys())

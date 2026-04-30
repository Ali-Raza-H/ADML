# ADML — AutoDesign Markup Language
## Full Specification, Architecture & Development Document
**Version:** 0.1 Draft  
**Status:** Pre-development / Concept  
**Author:** Open Source Initiative  
**Licence:** MIT (planned)

---

## Table of Contents

1. [The Core Idea](#1-the-core-idea)
2. [The Problem ADML Solves](#2-the-problem-adml-solves)
3. [How ADML Works — The Mental Model](#3-how-adml-works--the-mental-model)
4. [Language Design — Syntax & Structure](#4-language-design--syntax--structure)
5. [The Abstract Design Tree (ADT)](#5-the-abstract-design-tree-adt)
6. [Renderer Architecture](#6-renderer-architecture)
7. [Target Output Formats](#7-target-output-formats)
8. [Tech Stack Recommendations](#8-tech-stack-recommendations)
9. [Full Ecosystem — Agent + IDE + Compiler](#9-full-ecosystem--agent--ide--compiler)
10. [Development Roadmap](#10-development-roadmap)
11. [Prior Art & References](#11-prior-art--references)
12. [Open Questions & Design Decisions](#12-open-questions--design-decisions)

---

## 1. The Core Idea

ADML is a **declarative markup language for visual design**. It does for design tools what HTML and CSS did for web browsers — it provides a clean, human-readable, AI-friendly text format that compiles into professional design outputs across multiple formats.

Instead of wrestling with coordinate systems, proprietary binary formats, or GUI automation, you write intent-based markup:

```adml
@canvas(width=1920px, height=1080px, units=px)

slide("hero") {
  background: gradient(#1a1a2e → #16213e, direction=diagonal)

  text("AutoDesign Markup Language") {
    font: "Inter" bold
    size: 72px
    color: #ffffff
    position: center
    animate: fadeIn(0.4s)
  }

  text("Write once. Render anywhere.") {
    font: "Inter" regular
    size: 28px
    color: rgba(255, 255, 255, 0.7)
    position: center-bottom(offset=80px)
  }

  shape(rectangle) {
    width: 120px
    height: 4px
    fill: #4f46e5
    position: center(offset-y=20px)
    corner-radius: 2px
  }
}
```

This single file compiles to:
- `.pptx` (PowerPoint)
- `.pdf` (Print-ready)
- `.svg` (Vector)
- `.indd` / IDML (InDesign)
- `.html` (Web preview)
- Figma API (via REST)
- `.docx` (Word, for document-type layouts)

---

## 2. The Problem ADML Solves

### Why AI Fails at Design Tools Today

When you ask an AI to create a PowerPoint or Illustrator file, the results are poor. The reason is structural:

| Format | Nature | AI Behaviour |
|---|---|---|
| HTML/CSS | Intent-based, declarative | AI excels — describes what things *are* |
| ADML | Intent-based, declarative | AI will excel — same principle |
| PowerPoint | Absolute coordinates, XML blob | AI guesses pixel positions — fails |
| Illustrator | Bezier paths, anchor points | AI hallucinates curve data — unusable |
| InDesign | Complex layout engine, master pages | AI has no model of text flow rules |

The root problem: **design formats describe where things are, not what they are.** AI thinks in semantics and intent, not pixel coordinates.

ADML bridges this gap. The AI writes semantic markup. The ADML compiler resolves coordinates, layout rules, and format-specific encoding.

### The Gap in the Ecosystem

| Tool | Solves |
|---|---|
| HTML/CSS | Web layout — fully solved |
| Typst | Academic/print documents — largely solved |
| Mermaid | Diagrams — solved |
| Slidev / reveal.js | Web-based presentations — solved |
| **ADML** | **Professional design (print, presentations, vector, layout) — UNSOLVED** |

Nobody has built a universal declarative language that targets `.pptx`, `.indd`, `.ai`, `.pdf`, and `.figma` from a single source. This is the gap ADML fills.

---

## 3. How ADML Works — The Mental Model

### The Pipeline

```
Developer / AI writes .adml file
            ↓
      ADML Parser
  (text → token stream)
            ↓
    Semantic Analyser
  (validate, resolve vars, imports)
            ↓
  Abstract Design Tree (ADT)
  (format-agnostic object tree)
            ↓
    ┌────┬────┬────┬────┬────┬────┐
    ↓    ↓    ↓    ↓    ↓    ↓    ↓
  PPTX SVG  PDF IDML HTML FIGMA DOCX
renderer×6 (each translates ADT to format)
            ↓
      Output files
```

### The Key Insight — Intent vs Position

ADML stores **intent**, not coordinates. The renderer resolves positions.

```adml
# ADML — intent based
text("Hello") {
  position: center          ← "I want this centred"
  size: 48px
}

# What python-pptx receives (resolved by renderer)
left = (slide_width - text_width) / 2
top  = (slide_height - text_height) / 2
```

This means the same ADML file produces correctly positioned elements regardless of target format — a `.pptx` slide is 10 inches wide, an InDesign page might be A4, and the renderer handles both.

---

## 4. Language Design — Syntax & Structure

### Design Principles

1. **Readable by humans and AI alike** — no XML verbosity, no binary blobs
2. **CSS-influenced** — leverage universal familiarity with CSS property syntax
3. **Hierarchical** — elements nest inside containers, just like HTML
4. **Variables and tokens** — define once, use everywhere (like CSS custom properties)
5. **Import system** — reusable components and templates
6. **Comments** — full line and inline comment support

### File Structure

```adml
# ADML File Structure

@version(1.0)
@canvas(type=presentation, width=1920px, height=1080px)

# ── Variables / Design Tokens ──────────────────────────────
@vars {
  --primary:    #4f46e5
  --secondary:  #06b6d4
  --text-dark:  #1e1b4b
  --text-light: #ffffff
  --font-main:  "Inter"
  --font-mono:  "JetBrains Mono"
}

# ── Component Definitions ──────────────────────────────────
@component "title-block"(title, subtitle) {
  text($title) {
    font: var(--font-main) bold
    size: 64px
    color: var(--text-light)
    position: center-top(offset=120px)
  }
  text($subtitle) {
    font: var(--font-main) regular
    size: 24px
    color: rgba(255,255,255,0.7)
    position: center-top(offset=200px)
  }
}

# ── Import External Files ──────────────────────────────────
@import "brand/colours.adml"
@import "components/chart-styles.adml"

# ── Slides / Pages ────────────────────────────────────────
slide("intro") {
  background: gradient(var(--primary) → #1e1b4b)
  use("title-block", title="Welcome", subtitle="Q3 Review 2025")
}

slide("content") {
  layout: two-column(ratio=60:40, gap=40px)
  background: #ffffff

  column(left) {
    text("Key Findings") {
      font: var(--font-main) bold
      size: 36px
      color: var(--text-dark)
      margin-bottom: 24px
    }
    list(bullet) {
      item("Revenue up 24% YoY")
      item("New markets in 6 countries")
      item("NPS score 72 (+8)")
    }
  }

  column(right) {
    chart(bar) {
      data: [42, 58, 73, 91, 104]
      labels: ["Q3 '24", "Q4 '24", "Q1 '25", "Q2 '25", "Q3 '25"]
      colour: var(--primary)
      title: "Revenue ($M)"
    }
  }
}
```

### Element Types

#### Layout Elements
```adml
slide(id)         ← presentation slide / document page
section(id)       ← InDesign section / grouped region
column(side)      ← column within a layout
grid(cols, rows)  ← CSS-style grid container
group(id)         ← logical grouping of elements
frame(id)         ← InDesign-style text/image frame
```

#### Content Elements
```adml
text(content)         ← text block
heading(level, text)  ← h1-h6 equivalent
list(type)            ← bullet / numbered / custom
image(src)            ← raster image
vector(src)           ← SVG / AI vector asset
chart(type)           ← bar / line / pie / scatter
table(rows, cols)     ← data table
code(lang, content)   ← code block with syntax highlighting
divider               ← horizontal rule
spacer(height)        ← vertical whitespace
```

#### Shape Elements
```adml
shape(type) {
  # type = rectangle | circle | ellipse | polygon | line | arrow | star
  width: 200px
  height: 200px
  fill: #4f46e5
  stroke: #312e81 2px
  corner-radius: 8px
  opacity: 0.9
  shadow: drop(x=4px, y=4px, blur=12px, colour=rgba(0,0,0,0.3))
}
```

#### Typography System
```adml
text("The quick brown fox") {
  font: "Inter" bold italic        ← family weight style
  size: 48px
  color: #1e1b4b
  line-height: 1.4
  letter-spacing: -0.02em
  align: left | center | right | justify
  transform: uppercase | lowercase | capitalise
  decoration: underline | strikethrough
  max-width: 800px
  overflow: clip | wrap | scroll
}
```

#### Layout System — Position
```adml
# Absolute
position: absolute(x=100px, y=200px)

# Relative / Semantic (preferred)
position: center
position: top-left(margin=40px)
position: bottom-right(margin=40px)
position: center-top(offset=120px)
position: center-bottom(offset=80px)

# Flow (for document layouts)
position: flow         ← follows document text flow
position: float-right  ← text wraps around
position: full-bleed   ← edge to edge, ignores margins
```

#### Animation (for presentation formats)
```adml
animate: fadeIn(duration=0.5s, delay=0.2s)
animate: slideIn(from=left, duration=0.4s)
animate: scaleIn(origin=center, duration=0.3s)
animate: sequence(children, stagger=0.1s)  ← animate children one by one
```

### Canvas Types

The `@canvas` declaration tells ADML what kind of document you're building, which affects layout defaults:

```adml
@canvas(type=presentation, width=1920px, height=1080px)   ← 16:9 slide deck
@canvas(type=presentation, width=2560px, height=1440px)   ← QHD presentation
@canvas(type=document, size=A4, orientation=portrait)     ← flowing document
@canvas(type=document, size=letter, columns=2)            ← two-column layout
@canvas(type=vector, width=800px, height=600px)           ← illustration / artwork
@canvas(type=poster, width=594mm, height=841mm)           ← A1 poster (print)
@canvas(type=social, preset=instagram-square)             ← 1080×1080 social asset
@canvas(type=social, preset=linkedin-banner)              ← LinkedIn header
```

---

## 5. The Abstract Design Tree (ADT)

The ADT is the internal object model — format-agnostic, pure Python objects. This is what the parser produces and what every renderer consumes.

### Core Classes

```python
# adml/adt/core.py

from dataclasses import dataclass, field
from typing import Optional, Union
from enum import Enum

class CanvasType(Enum):
    PRESENTATION = "presentation"
    DOCUMENT     = "document"
    VECTOR       = "vector"
    POSTER       = "poster"
    SOCIAL       = "social"

class PositionType(Enum):
    ABSOLUTE  = "absolute"
    CENTER    = "center"
    SEMANTIC  = "semantic"
    FLOW      = "flow"

@dataclass
class Dimensions:
    width:  float         # always stored in points internally
    height: float
    unit:   str = "pt"    # px | pt | mm | in — normalised on parse

@dataclass
class Colour:
    r: int
    g: int
    b: int
    a: float = 1.0

    @staticmethod
    def from_hex(hex: str) -> "Colour": ...

@dataclass
class Position:
    type:     PositionType
    x:        Optional[float] = None   # used for ABSOLUTE
    y:        Optional[float] = None
    semantic: Optional[str]  = None    # "center", "top-left", etc.
    offset_x: float = 0.0
    offset_y: float = 0.0
    margin:   float = 0.0

@dataclass
class Font:
    family:  str
    size:    float          # in points
    weight:  str = "regular"
    style:   str = "normal"
    colour:  Colour = field(default_factory=lambda: Colour(0,0,0))
    line_height:    float = 1.4
    letter_spacing: float = 0.0
    align:   str = "left"

@dataclass
class Shadow:
    x:      float
    y:      float
    blur:   float
    colour: Colour

@dataclass
class Fill:
    type:    str              # "solid" | "gradient" | "image" | "none"
    colour:  Optional[Colour] = None
    colours: Optional[list[Colour]] = None   # for gradient
    direction: Optional[str] = None
    image:   Optional[str] = None

# ── Elements ────────────────────────────────────────────────────────────

@dataclass
class Element:
    id:       Optional[str] = None
    position: Optional[Position] = None
    size:     Optional[Dimensions] = None
    opacity:  float = 1.0
    shadow:   Optional[Shadow] = None
    animate:  Optional[dict] = None
    children: list["Element"] = field(default_factory=list)

@dataclass
class TextElement(Element):
    content:  str = ""
    font:     Font = field(default_factory=Font)
    max_width: Optional[float] = None
    overflow: str = "wrap"

@dataclass
class ShapeElement(Element):
    shape_type:    str = "rectangle"      # rectangle|circle|line|polygon
    fill:          Fill = field(default_factory=Fill)
    stroke_colour: Optional[Colour] = None
    stroke_width:  float = 0.0
    corner_radius: float = 0.0

@dataclass
class ImageElement(Element):
    src:     str = ""
    fit:     str = "contain"              # contain|cover|fill|none
    alt:     str = ""

@dataclass
class ChartElement(Element):
    chart_type: str = "bar"
    data:       list[float] = field(default_factory=list)
    labels:     list[str]   = field(default_factory=list)
    title:      str = ""
    colour:     Optional[Colour] = None

@dataclass
class ListElement(Element):
    list_type: str = "bullet"             # bullet|numbered|custom
    items:     list[str] = field(default_factory=list)
    font:      Font = field(default_factory=Font)

@dataclass
class GroupElement(Element):
    layout:    str = "free"              # free|grid|row|column
    gap:       float = 0.0

# ── Container (Slide / Page) ────────────────────────────────────────────

@dataclass
class Container:
    id:         str
    background: Fill
    elements:   list[Element] = field(default_factory=list)
    notes:      str = ""                 # speaker notes (presentations)
    layout:     Optional[str] = None     # "two-column", "grid", etc.

# ── Document Root ────────────────────────────────────────────────────────

@dataclass
class DesignDocument:
    version:    str
    canvas:     CanvasType
    dimensions: Dimensions
    variables:  dict[str, str]
    components: dict[str, list[Element]]
    containers: list[Container]           # slides or pages
    metadata:   dict[str, str]
```

---

## 6. Renderer Architecture

Each renderer takes a `DesignDocument` ADT and outputs bytes or a file.

### Base Renderer Interface

```python
# adml/renderers/base.py

from abc import ABC, abstractmethod
from adml.adt.core import DesignDocument

class BaseRenderer(ABC):

    def __init__(self, doc: DesignDocument):
        self.doc = doc

    @abstractmethod
    def render(self) -> bytes:
        """Render the document to bytes in target format."""
        ...

    def resolve_position(self, element, container_dims) -> tuple[float, float]:
        """
        Convert semantic positions to absolute coordinates.
        This is shared logic used by every renderer.
        """
        pos = element.position
        cw, ch = container_dims.width, container_dims.height
        ew = element.size.width  if element.size else 0
        eh = element.size.height if element.size else 0

        match pos.semantic:
            case "center":
                return (cw - ew) / 2, (ch - eh) / 2
            case "center-top":
                return (cw - ew) / 2, pos.offset_y
            case "center-bottom":
                return (cw - ew) / 2, ch - eh - pos.offset_y
            case "top-left":
                return pos.margin, pos.margin
            case "bottom-right":
                return cw - ew - pos.margin, ch - eh - pos.margin
            case _:
                return pos.x or 0, pos.y or 0
```

### PowerPoint Renderer

```python
# adml/renderers/pptx_renderer.py

from pptx import Presentation
from pptx.util import Pt, Emu, Inches
from pptx.dml.color import RGBColor
from adml.renderers.base import BaseRenderer

class PowerPointRenderer(BaseRenderer):

    def render(self) -> bytes:
        prs = Presentation()
        prs.slide_width  = Emu(self.doc.dimensions.width  * 12700)
        prs.slide_height = Emu(self.doc.dimensions.height * 12700)

        blank_layout = prs.slide_layouts[6]  # blank layout

        for container in self.doc.containers:
            slide = prs.slides.add_slide(blank_layout)
            self._render_background(slide, container.background)
            for element in container.elements:
                self._render_element(slide, element, self.doc.dimensions)

        from io import BytesIO
        buf = BytesIO()
        prs.save(buf)
        return buf.getvalue()

    def _render_element(self, slide, element, canvas_dims):
        x, y = self.resolve_position(element, canvas_dims)
        match element:
            case TextElement():
                self._add_text(slide, element, x, y)
            case ShapeElement():
                self._add_shape(slide, element, x, y)
            case ImageElement():
                self._add_image(slide, element, x, y)
            case ChartElement():
                self._add_chart(slide, element, x, y)
            case GroupElement():
                for child in element.children:
                    self._render_element(slide, child, canvas_dims)
```

### SVG / Illustrator Renderer

```python
# adml/renderers/svg_renderer.py
# SVG is the natural target for .ai — Illustrator opens SVG natively
# and ADML can produce clean, layered SVG with proper IDs

import xml.etree.ElementTree as ET
from adml.renderers.base import BaseRenderer

class SVGRenderer(BaseRenderer):

    def render(self) -> bytes:
        w = self.doc.dimensions.width
        h = self.doc.dimensions.height

        svg = ET.Element("svg", {
            "xmlns":   "http://www.w3.org/2000/svg",
            "viewBox": f"0 0 {w} {h}",
            "width":   str(w),
            "height":  str(h),
        })

        for container in self.doc.containers:
            group = ET.SubElement(svg, "g", {"id": container.id})
            self._render_background(group, container, w, h)
            for element in container.elements:
                self._render_element(group, element, w, h)

        return ET.tostring(svg, encoding="unicode").encode()
```

### InDesign (IDML) Renderer

IDML is a ZIP archive of XML files. You write it directly — no InDesign licence needed.

```python
# adml/renderers/idml_renderer.py
# IDML = ZIP of XML files
# Key files: designmap.xml, spreads/Spread_*.xml, stories/Story_*.xml

import zipfile
from io import BytesIO
from adml.renderers.base import BaseRenderer

class IDMLRenderer(BaseRenderer):

    def render(self) -> bytes:
        buf = BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("mimetype", "application/vnd.adobe.indesign-idml-package")
            zf.writestr("designmap.xml",    self._build_designmap())
            zf.writestr("Resources/Fonts.xml",   self._build_fonts())
            zf.writestr("Resources/Styles.xml",  self._build_styles())

            for i, container in enumerate(self.doc.containers):
                spread_xml = self._build_spread(container, i)
                zf.writestr(f"Spreads/Spread_{i}.xml", spread_xml)
                story_xml  = self._build_stories(container, i)
                zf.writestr(f"Stories/Story_{i}.xml", story_xml)

        return buf.getvalue()
```

### Renderer Registry

```python
# adml/renderers/__init__.py

from adml.renderers.pptx_renderer  import PowerPointRenderer
from adml.renderers.svg_renderer   import SVGRenderer
from adml.renderers.pdf_renderer   import PDFRenderer
from adml.renderers.idml_renderer  import IDMLRenderer
from adml.renderers.html_renderer  import HTMLRenderer
from adml.renderers.figma_renderer import FigmaRenderer
from adml.renderers.docx_renderer  import WordRenderer

RENDERERS = {
    "pptx":  PowerPointRenderer,
    "svg":   SVGRenderer,
    "ai":    SVGRenderer,        # Illustrator uses SVG as base
    "pdf":   PDFRenderer,
    "idml":  IDMLRenderer,
    "html":  HTMLRenderer,
    "figma": FigmaRenderer,      # pushes via Figma REST API
    "docx":  WordRenderer,
}

def render(doc, format: str) -> bytes:
    renderer_class = RENDERERS.get(format)
    if not renderer_class:
        raise ValueError(f"Unknown format: {format}")
    return renderer_class(doc).render()
```

---

## 7. Target Output Formats

### PowerPoint (.pptx)
- **Library:** `python-pptx`
- **Format:** ZIP of OOXML (Office Open XML)
- **Supports:** All element types, animations, speaker notes, master slides
- **Limitations:** Charts need careful EMU unit handling; animations are PowerPoint-specific
- **Notes:** EMU (English Metric Units): 914400 EMU = 1 inch = 72pt

### Illustrator (.ai / .svg)
- **Library:** SVG generation via `lxml` or `xml.etree`
- **Format:** .ai files are PostScript wrappers around SVG; export clean SVG, Illustrator opens natively
- **Supports:** Shapes, paths, groups, text, gradients, layers
- **Notes:** Use `<g>` elements as Illustrator layers. Set `inkscape:label` for layer names (compatible with both Inkscape and Illustrator)

### InDesign (.indd / IDML)
- **Library:** Direct XML generation + zipfile
- **Format:** IDML = ZIP of XML
- **Supports:** Master pages, text frames, linked images, paragraph styles, layers
- **Adobe spec:** https://wwwimages.adobe.com/www.adobe.com/content/dam/acom/en/devnet/indesign/sdk/cs6/idml/idml-specification.pdf
- **Notes:** InDesign opens IDML natively. This is how templates and snippets work internally.

### PDF
- **Library:** `reportlab` for generation; `weasyprint` for HTML→PDF
- **Format:** ISO 32000 standard
- **Supports:** Everything except animations
- **Notes:** Two approaches: generate directly via ReportLab (full control) or render HTML→PDF via WeasyPrint (easier for complex layouts)

### Figma
- **Library:** Figma REST API + `httpx`
- **Format:** JSON via REST API calls
- **Supports:** Frames, components, text, shapes, auto-layout
- **Notes:** Requires Figma API token. Uses `POST /v1/files/{file_key}/nodes` to write. Figma Plugin API offers deeper access via the editor.

### Word (.docx)
- **Library:** `python-docx` or `docx` (Node.js)
- **Format:** ZIP of OOXML
- **Supports:** Text flow, tables, headers/footers, styles, tracked changes
- **Notes:** Best for document-type canvases; presentations map awkwardly to Word

### HTML (Preview / Web)
- **Library:** Standard Python string templating / Jinja2
- **Format:** HTML + CSS + optional JS
- **Supports:** All visual elements; animations via CSS/JS
- **Notes:** Used for live preview in the IDE. Also a valid final output for web presentations

---

## 8. Tech Stack Recommendations

This stack is chosen for AI-assisted development — maximum library support, strong documentation, AI code generation quality, and ecosystem maturity.

### Primary Language: Python

Python is the correct choice for this project because:
- All target format libraries (`python-pptx`, `python-docx`, `reportlab`, `psd-tools`, `lxml`) are Python-first
- The best parser generators (Lark, ANTLR Python target) have Python bindings
- AI code generation for Python is the most reliable of any language
- Cross-platform (Windows and Linux) without friction
- Fastest iteration speed for a solo/small team

### Core Stack

| Component | Technology | Why |
|---|---|---|
| **Language** | Python 3.12+ | Best library ecosystem for format rendering |
| **Parser / Grammar** | Lark (PEG grammar) | Clean, pure Python, excellent error messages |
| **AST / ADT** | Python dataclasses | Zero dependencies, IDE-friendly, serialisable |
| **PPTX output** | python-pptx | Mature, full-featured, well documented |
| **DOCX output** | python-docx | Same ecosystem as python-pptx |
| **SVG / AI output** | lxml + svgwrite | Full SVG spec support |
| **PDF output** | reportlab | Industry standard for PDF generation in Python |
| **IDML output** | zipfile + lxml | Write IDML XML directly — no library needed |
| **Figma output** | httpx + Figma REST API | Official API |
| **Charts** | matplotlib → SVG/PNG | Then embed into target format |
| **CLI interface** | Typer | Modern, type-annotated CLI framework |
| **Config** | TOML (tomllib, built into Python 3.11+) | Clean config format |
| **Testing** | pytest | Standard |
| **Packaging** | pyproject.toml + hatchling | Modern Python packaging |

### IDE / Preview Tool Stack

| Component | Technology | Why |
|---|---|---|
| **Editor framework** | VS Code Extension API | Largest user base, best extension ecosystem |
| **Syntax highlighting** | TextMate grammar (JSON) | Standard for VS Code extensions |
| **Language server** | pygls (Python LSP framework) | Autocomplete, error squiggles, hover docs |
| **Live preview** | Webview (HTML renderer output) | VS Code webview panel renders HTML natively |
| **Preview server** | Flask or FastAPI (local) | Watches file, re-renders on save, pushes to webview |

### Agent Integration Stack

| Component | Technology | Why |
|---|---|---|
| **LLM backend** | Ollama (local) | Self-hosted, private, no API costs |
| **Agent framework** | Custom (as discussed) | Full control over tool calling loop |
| **ADML generation tool** | ADML compiler as agent tool | Agent writes .adml, compiler renders it |
| **Model recommendation** | qwen2.5:14b or mistral-nemo | Best instruction following for structured output |

### Project Structure

```
adml/
├── pyproject.toml             ← packaging and dependencies
├── README.md
├── spec/
│   └── ADML_Specification.md  ← this document
│
├── adml/                      ← main Python package
│   ├── __init__.py
│   ├── cli.py                 ← typer CLI entry point
│   ├── grammar/
│   │   ├── adml.lark          ← Lark PEG grammar definition
│   │   └── parser.py          ← parser wrapper + error handling
│   ├── adt/
│   │   ├── core.py            ← all dataclasses (DesignDocument, Element, etc.)
│   │   ├── resolver.py        ← variable resolution, component expansion
│   │   └── validator.py       ← semantic validation before rendering
│   ├── renderers/
│   │   ├── __init__.py        ← renderer registry + render() function
│   │   ├── base.py            ← BaseRenderer + shared position resolver
│   │   ├── pptx_renderer.py
│   │   ├── svg_renderer.py    ← also used for .ai output
│   │   ├── pdf_renderer.py
│   │   ├── idml_renderer.py
│   │   ├── html_renderer.py   ← used for IDE live preview
│   │   ├── figma_renderer.py
│   │   └── docx_renderer.py
│   └── utils/
│       ├── units.py           ← unit conversion (px→pt→mm→emu→etc.)
│       ├── colours.py         ← colour parsing and conversion
│       └── fonts.py           ← font resolution and fallback
│
├── vscode-adml/               ← VS Code extension
│   ├── package.json
│   ├── syntaxes/
│   │   └── adml.tmLanguage.json
│   ├── src/
│   │   ├── extension.ts       ← extension entry point
│   │   ├── preview.ts         ← live preview webview
│   │   └── lsp_client.ts      ← connects to Python LSP server
│   └── language-server/
│       └── server.py          ← pygls LSP server
│
├── agent/                     ← the AI agent that generates ADML
│   ├── main.py                ← CLI REPL
│   ├── agent.py               ← agent loop
│   ├── llm/
│   │   └── ollama.py
│   └── tools/
│       ├── adml_writer.py     ← tool: generate ADML from description
│       ├── adml_compiler.py   ← tool: compile ADML to output format
│       └── adml_editor.py     ← tool: edit specific elements in ADML
│
└── tests/
    ├── test_parser.py
    ├── test_adt.py
    ├── test_renderers/
    │   ├── test_pptx.py
    │   ├── test_svg.py
    │   └── test_idml.py
    └── fixtures/
        └── *.adml             ← sample ADML files for testing
```

---

## 9. Full Ecosystem — Agent + IDE + Compiler

### How the Three Components Work Together

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER WORKFLOWS                           │
├────────────────┬────────────────────┬───────────────────────────┤
│  Write by hand │  AI agent creates  │  IDE with live preview    │
│  in .adml file │  .adml from prompt │  and autocomplete         │
└───────┬────────┴─────────┬──────────┴──────────────┬────────────┘
        │                  │                          │
        └──────────────────▼──────────────────────────┘
                     ADML Compiler
               (parser → ADT → renderer)
                           │
         ┌─────────────────┼─────────────────┐
         ↓                 ↓                 ↓
       .pptx             .svg             .idml
       .docx             .pdf             .html
                       + Figma API
```

### Agent — How It Generates ADML

The agent's job is to turn natural language into valid ADML. It does this via a dedicated tool:

**Agent tool: `generate_design`**
```python
def generate_design(description: str, canvas_type: str, output_format: str) -> dict:
    """
    1. Send description to Ollama with ADML system prompt
    2. Ollama generates .adml markup
    3. Compiler validates and renders
    4. Returns path to output file
    """
```

**Agent system prompt (the crucial part):**
```
You are an expert ADML designer. When asked to create designs, respond 
ONLY with valid ADML markup. Do not explain. Do not add prose.
Follow the ADML specification exactly.

ADML is a declarative design language where you express intent, not 
coordinates. Use semantic positions like `center`, `top-left(margin=40px)`.
Use variables from @vars blocks. Use components for repeated elements.

The user will describe what they want. You produce the ADML.
```

This is why ADML is so powerful for AI — the model writes markup, not pixel coordinates. The same way AI can write HTML fluently, it will write ADML fluently.

### IDE Extension Features

The VS Code extension provides:

**Syntax Highlighting**
- `.adml` files get full syntax colouring
- Keywords, values, element types, variables all coloured distinctly

**Language Server (LSP)**
- Autocomplete for element types, properties, values
- Error squiggles for invalid syntax or unknown variables
- Hover documentation (hover over `position:` → see all valid values)
- Go to definition for `@component` references
- Rename symbol for variables and components

**Live Preview Panel**
- Split pane: ADML source on left, rendered HTML preview on right
- Re-renders on every save (or optionally on every keystroke)
- Format selector: toggle between HTML preview, SVG preview
- Zoom and pan controls

**Export Command**
- Right-click → Export As → [select format]
- Or: `Ctrl+Shift+P` → "ADML: Export" → choose format
- Runs the CLI compiler and opens the output file

---

## 10. Development Roadmap

### Phase 1 — Foundation (Weeks 1–4)
**Goal:** A working parser and one renderer

- [ ] Define the Lark grammar for core syntax
- [ ] Build the parser → ADT pipeline
- [ ] Build unit conversion utilities (px, pt, mm, in, emu)
- [ ] Build colour parsing utility
- [ ] Implement `PowerPointRenderer` (shapes, text, images, backgrounds)
- [ ] Build the CLI (`adml compile input.adml --format pptx`)
- [ ] Write 10 fixture .adml files as test cases
- [ ] Set up pytest suite
- [ ] Publish to GitHub as open source

**Milestone:** `adml compile deck.adml --format pptx` produces a valid .pptx

### Phase 2 — More Renderers (Weeks 5–8)
**Goal:** All 6 target formats working at basic level

- [ ] SVG renderer (also covers .ai output)
- [ ] HTML renderer (needed for IDE preview)
- [ ] PDF renderer (reportlab)
- [ ] IDML renderer (InDesign)
- [ ] Word renderer (python-docx)
- [ ] Figma renderer (REST API)
- [ ] Cross-renderer position resolver (shared base logic)

**Milestone:** Same .adml compiles to all 6 formats correctly

### Phase 3 — Language Completeness (Weeks 9–12)
**Goal:** Full language feature set

- [ ] Variable system (`@vars`, `var()` references)
- [ ] Component system (`@component`, `use()`)
- [ ] Import system (`@import`)
- [ ] Layout system (grid, two-column, flow)
- [ ] Animation definitions (pptx and HTML targets)
- [ ] Chart element (matplotlib → embedded)
- [ ] List element with proper bullet/number rendering
- [ ] Table element
- [ ] Font system with fallback resolution

**Milestone:** Complex real-world documents producible in ADML

### Phase 4 — IDE Extension (Weeks 13–18)
**Goal:** VS Code extension on the marketplace

- [ ] TextMate grammar for syntax highlighting
- [ ] Publish extension scaffolding (vsce)
- [ ] Live preview webview (HTML renderer output)
- [ ] File watcher → auto re-render
- [ ] pygls language server
- [ ] Autocomplete for element types and properties
- [ ] Error highlighting
- [ ] Export command palette
- [ ] Publish to VS Code Marketplace

**Milestone:** Extension installable from VS Code marketplace

### Phase 5 — Agent Integration (Weeks 19–22)
**Goal:** AI agent that generates ADML from natural language

- [ ] Build agent core (Ollama backend, tool loop)
- [ ] Create `generate_design` tool
- [ ] Create `edit_element` tool (find and modify specific elements)
- [ ] Create `compile_design` tool
- [ ] Craft ADML system prompt for LLMs
- [ ] Test with qwen2.5:14b, mistral-nemo, llama3.3
- [ ] Build agent CLI with interactive mode
- [ ] Document prompt patterns for best results

**Milestone:** "Create me a 10-slide pitch deck about renewable energy" → valid .pptx

### Phase 6 — Polish & Community (Ongoing)
- [ ] ADML playground website (browser-based editor + preview)
- [ ] Template library (50+ starter templates in ADML)
- [ ] Plugin system for custom renderers
- [ ] Full specification documentation website
- [ ] Video tutorials
- [ ] Community Discord

---

## 11. Prior Art & References

### Languages to Learn From

| Project | What to Study |
|---|---|
| **Typst** | How a markup → layout compiler works end to end. Study their IR design. |
| **Mermaid** | How a simple DSL compiles to SVG. Good reference for grammar design. |
| **Sass/SCSS** | How a CSS superset with variables/mixins compiles down. |
| **Pug/Jade** | Template language → HTML. Shows how components and includes work. |
| **MDX** | Markdown + JSX. Shows how to embed logic in markup. |
| **Slidev** | Markdown → presentations. The closest existing thing to ADML for slides. |

### Format Specifications

| Format | Where to find the spec |
|---|---|
| OOXML (pptx/docx) | ECMA-376 standard — ecma-international.org |
| IDML | Adobe Developer — "IDML Specification" PDF (free download) |
| SVG | W3C SVG 2.0 specification — w3.org |
| PDF | ISO 32000-2 — available from Adobe for free |
| Figma REST API | figma.com/developers/api |

### Python Libraries — Documentation

| Library | Purpose | Docs |
|---|---|---|
| `python-pptx` | PowerPoint | python-pptx.readthedocs.io |
| `python-docx` | Word | python-docx.readthedocs.io |
| `lark-parser` | Grammar / parsing | lark-parser.readthedocs.io |
| `reportlab` | PDF | reportlab.com/docs |
| `svgwrite` | SVG | svgwrite.readthedocs.io |
| `lxml` | XML manipulation | lxml.de |
| `matplotlib` | Charts | matplotlib.org |
| `typer` | CLI | typer.tiangolo.com |
| `pygls` | LSP server | pygls.readthedocs.io |

---

## 12. Open Questions & Design Decisions

These are the unresolved design choices that need decisions before or during Phase 1 development. Record decisions here as they are made.

### Q1: File Extension
What file extension does ADML use?
- `.adml` — matches the language name ✓ (recommended)
- `.adm` — shorter
- `.design` — more semantic

**Decision:** _Pending_

### Q2: Syntax Style
Should the language use curly-brace blocks (C-style) or indentation (Python-style)?

```adml
# Option A — curly braces (chosen above)
slide("hero") {
  text("Hello") { size: 48px }
}

# Option B — indented
slide "hero":
  text "Hello":
    size: 48px
```

Curly braces are more familiar to most developers and easier to parse unambiguously.

**Decision:** _Curly braces recommended_

### Q3: Unit System
Default unit when none specified?

- `px` — most familiar for screen designers
- `pt` — most familiar for print designers
- Let the `@canvas` type determine the default (px for screen, mm for print)

**Decision:** _Pending_

### Q4: Colour Format Support
Which colour formats to support?

- Hex: `#4f46e5` ✓
- RGB: `rgb(79, 70, 229)` ✓
- RGBA: `rgba(79, 70, 229, 0.8)` ✓
- HSL: `hsl(244, 63%, 59%)` — nice to have
- Named colours: `red`, `blue` — useful for prototyping
- Design token references: `var(--primary)` ✓

**Decision:** _All of the above recommended_

### Q5: Font Resolution
How does ADML handle fonts not installed on the system?

- Fail with a clear error message
- Fall back to a system default and warn
- Embed font lookup (download from Google Fonts?)
- Allow renderer-specific fallback maps in config

**Decision:** _Pending_

### Q6: Versioning and Format Stability
How do we handle breaking changes to the language?

- `@version(1.0)` declaration at top of every file
- Parser maintains backwards compatibility per version
- Deprecation warnings before removal

**Decision:** _Version declaration required — version 1.0 is the current target_

### Q7: Scripting / Logic
Should ADML support conditional logic or loops?

```adml
# Option: loop over data
@each $slide in $slides {
  slide($slide.id) {
    text($slide.title) { ... }
  }
}
```

This would make ADML a template language, not just a markup language. Adds complexity but enables data-driven documents.

**Decision:** _Defer to v2.0 — keep v1.0 purely declarative_

### Q8: Bi-directional Parsing
Should the compiler support reading existing .pptx/.docx files and converting them TO ADML?

This would allow: import an existing PowerPoint → get ADML → edit with AI → re-export.
Very powerful, but a significant additional engineering effort.

**Decision:** _Target for Phase 6 or later_

---

*Document version 0.1 — created for review and development planning.*  
*Update this document as design decisions are made and phases complete.*  
*All code samples are illustrative pseudocode until implementation begins.*

# adml-lang

AutoDesign Markup Language compiler.

ADML is a text-based declarative design language. You write markup that describes your design intent, and the ADML compiler generates output formats like PowerPoint (.pptx), SVG, and live HTML previews. It's designed to be AI-friendly, allowing models to generate markup rather than pixel values.

## Example

```adml
@version(1.0)
@canvas(type=presentation, width=1920, height=1080, units=px)

slide("hero") {
  background: #0f0f1a

  text("AutoDesign Markup Language") {
    font: "Inter" bold
    size: 72
    color: #ffffff
    position: center
  }
}
```

## Installation

```bash
pip install adml-lang
```

## Quick Start

1. Create a file named `presentation.adml`.
2. Write your ADML markup.
3. Compile to PowerPoint:
   ```bash
   adml compile presentation.adml --format pptx
   ```

## CLI Reference

| Command | Description |
|---|---|
| `adml compile <file> -f <format>` | Compile an ADML file to the specified output format |
| `adml validate <file>` | Validate an ADML file without rendering |
| `adml preview <file>` | Compile to HTML and open in the default browser |
| `adml formats` | List all available output formats |
| `adml info <file>` | Show information about an ADML file |

## Supported Formats

| Format | Extension | Description |
|---|---|---|
| PowerPoint | `.pptx` | Microsoft PowerPoint presentation |
| SVG | `.svg` | Scalable Vector Graphics |
| HTML | `.html` | Live preview in browser |

## Contributing
See CONTRIBUTING.md for more details.

## License
MIT

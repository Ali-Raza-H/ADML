import typer
import webbrowser
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table

from adml.grammar.parser import parse, ADMLSyntaxError
from adml.adt.resolver import resolve
from adml.adt.validator import validate as validate_doc
from adml.renderers import render as render_doc, available_formats

app = typer.Typer(
    name="adml",
    help="AutoDesign Markup Language compiler",
    add_completion=False
)
console = Console()

def _load_and_process(input_file: Path) -> tuple:
    if not input_file.exists():
        console.print(f"[red]Error:[/red] File '{input_file}' not found.")
        raise typer.Exit(1)
        
    source = input_file.read_text(encoding="utf-8")
    try:
        doc = parse(source)
    except ADMLSyntaxError as e:
        console.print(f"[red]Syntax Error:[/red]\n{e}")
        raise typer.Exit(1)
        
    doc = resolve(doc)
    result = validate_doc(doc)
    
    for warn in result.warnings:
        console.print(f"[yellow]Warning:[/yellow] {warn}")
    if result.errors:
        for err in result.errors:
            console.print(f"[red]Error:[/red] {err}")
        raise typer.Exit(1)
        
    return doc, result

@app.command()
def compile(
    input_file: Path = typer.Argument(..., help="Path to .adml file"),
    format: str = typer.Option("pptx", "--format", "-f", help="Output format: pptx, svg, html, ai"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path."),
    validate_only: bool = typer.Option(False, "--validate", help="Only validate the file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output")
):
    """Compile an ADML file to the specified output format."""
    doc, _ = _load_and_process(input_file)
    
    if validate_only:
        console.print("[green]Validation successful.[/green]")
        return
        
    if format not in available_formats():
        console.print(f"[red]Error:[/red] Unknown format '{format}'.")
        raise typer.Exit(1)
        
    if output is None:
        output = input_file.with_suffix(f".{format}")
        
    try:
        bytes_data = render_doc(doc, format)
        output.write_bytes(bytes_data)
        size_kb = len(bytes_data) / 1024
        console.print(f"[green]Success![/green] Rendered {output} ({size_kb:.1f} KB)")
    except Exception as e:
        console.print(f"[red]Rendering Error:[/red] {e}")
        raise typer.Exit(1)

@app.command(name="validate")
def validate_cmd(input_file: Path = typer.Argument(..., help="Path to .adml file")):
    """Validate an ADML file without rendering it."""
    _load_and_process(input_file)
    console.print("[green]Validation successful.[/green]")

@app.command()
def preview(input_file: Path = typer.Argument(..., help="Path to .adml file")):
    """Compile to HTML and open in the default browser."""
    doc, _ = _load_and_process(input_file)
    out_path = input_file.with_suffix(".html")
    bytes_data = render_doc(doc, "html")
    out_path.write_bytes(bytes_data)
    webbrowser.open(f"file://{out_path.absolute()}")
    console.print(f"[green]Preview opened in browser[/green]")

@app.command()
def formats():
    """List all available output formats."""
    console.print("Available formats:")
    for f in available_formats():
        console.print(f" - {f}")

@app.command()
def info(input_file: Path = typer.Argument(..., help="Path to .adml file")):
    """Show information about an ADML file."""
    doc, res = _load_and_process(input_file)
    
    table = Table(title=f"ADML Info: {input_file.name}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Version", doc.version)
    table.add_row("Canvas Type", doc.canvas_type.value)
    table.add_row("Dimensions", f"{doc.width}pt x {doc.height}pt")
    table.add_row("Slides", str(len(doc.slides)))
    table.add_row("Variables", str(len(doc.variables)))
    table.add_row("Validation", "Valid" if not res.errors else "Errors")
    
    console.print(table)

if __name__ == "__main__":
    app()

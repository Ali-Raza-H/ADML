# Contributing to ADML

Thank you for your interest in contributing to ADML (AutoDesign Markup Language)! We welcome contributions from everyone, whether it's fixing a bug, improving documentation, or adding new features.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct (please be respectful and professional in all interactions).

## How Can I Contribute?

### Reporting Bugs
- Search existing issues to see if the bug has already been reported.
- If not, open a new issue with a clear title and description.
- Include steps to reproduce the bug and the version of ADML you are using.
- Provide a minimal `.adml` file that demonstrates the issue.

### Suggesting Enhancements
- Open a new issue describing the proposed enhancement.
- Explain why this feature would be useful and how it fits into the ADML vision.
- If possible, provide examples of the proposed syntax or behavior.

### Pull Requests
- Fork the repository and create your branch from `main`.
- If you've added code that should be tested, add tests.
- If you've changed APIs, update the documentation.
- Ensure the test suite passes.
- Make sure your code follows the project's coding style.

## Setting Up Your Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/ADML.git
   cd ADML
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies in editable mode with dev tools:**
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Project Structure
- `adml/grammar/`: Lark grammar definitions (`adml.lark`) and parser logic.
- `adml/adt/`: The Abstract Design Tree (format-agnostic object model).
- `adml/renderers/`: Logic for converting the ADT to output formats (PPTX, SVG, etc.).
- `adml/utils/`: Shared utilities for units, colors, and fonts.
- `tests/`: Comprehensive test suite.

### Running Tests
We use `pytest` for testing. Run the full suite with:
```bash
pytest
```

To run a specific test file:
```bash
pytest tests/test_parser.py
```

### Coding Standards
- **Python Style:** Follow PEP 8 guidelines.
- **Type Hints:** Use type hints for all function signatures and complex variables.
- **Documentation:** Use Google-style docstrings for modules, classes, and functions.
- **Grammar:** If modifying the Lark grammar, ensure that the parser tests are updated and that the grammar remains clean and efficient.

## Architecture Overview

ADML follows a clear pipeline:
1. **Parser:** Reads `.adml` text and converts it into tokens using Lark.
2. **ADT (Abstract Design Tree):** The tokens are transformed into a tree of format-agnostic Python dataclasses.
3. **Resolver/Validator:** Variables are resolved, and the tree is validated for semantic correctness.
4. **Renderer:** The validated ADT is passed to a specific renderer (e.g., `PowerPointRenderer`) to generate the final output.

When adding a new feature, consider where it fits in this pipeline. Most visual features require changes to the grammar, the ADT, and all active renderers.

---

Thank you for contributing!

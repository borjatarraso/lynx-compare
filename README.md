# Lynx Compare

**Side-by-side fundamental analysis comparison tool**

[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-green.svg)](LICENSE)

Lynx Compare is part of the **Lince Investor** suite. It compares two
publicly traded companies across seven fundamental analysis sections:
valuation, profitability, solvency, growth, efficiency, moat, and
intrinsic value.

## Features

- **Seven comparison sections** -- valuation, profitability, solvency,
  growth, efficiency, moat indicators, and intrinsic value
- **40+ metrics** with directional rules (higher/lower is better depending
  on the metric)
- **Four interfaces** -- choose what fits your workflow:
  - **CLI** (default) for one-shot comparisons
  - **Interactive mode** (`-i`) with persistent session and inline commands
  - **Full-screen TUI** (`-tui`) built on [Textual](https://textual.textualize.io/)
  - **Graphical interface** (`-x`) with Catppuccin Mocha dark theme
- **REST API server** (`lynx-compare-server`) powered by Flask
- **Export** -- HTML, PDF (via weasyprint), and plain-text reports
- **Public API** -- `compare_companies()` and `compare_reports()` for
  library usage with `ComparisonView` wrapper
- **Comparability warnings** -- alerts for sector, industry, or tier
  mismatches between companies

## Installation

```bash
# Clone the repository
git clone https://github.com/borjatarraso/lynx-compare.git
cd lynx-compare

# Install in editable mode (creates the `lynx-compare` command)
pip install -e .
```

### Dependencies

| Package  | Purpose                           |
|----------|-----------------------------------|
| lynx-fa  | Fundamental analysis engine       |
| rich     | Terminal tables and formatting    |
| textual  | Full-screen TUI framework         |
| flask    | REST API server                   |

All dependencies are installed automatically via `pip install -e .`.

## Quick Start

```bash
# Compare two companies (production mode, uses cache)
lynx-compare -p AAPL MSFT

# Compare with fresh data
lynx-compare -t AAPL MSFT

# Force refresh in production mode
lynx-compare -p AAPL MSFT --refresh

# Launch interactive mode
lynx-compare -p -i

# Launch terminal UI
lynx-compare -p -tui

# Launch graphical interface
lynx-compare -p -x

# Export comparison to HTML
lynx-compare -p AAPL MSFT --export comparison.html
```

## Running Modes

| Flag | Data Source | Cache Behavior |
|------|------------|----------------|
| `-p` / `--production-mode` | `data/` from lynx-fa | Cache-first (reuses saved data) |
| `-t` / `--testing-mode` | `data_test/` from lynx-fa | Always fresh (never reads cache) |

## Interfaces

### CLI (default)

```bash
lynx-compare -p AAPL MSFT
```

Displays a three-column comparison with unicode arrows showing the winner
for each metric, color-coded section verdicts, and an overall winner.

### Interactive Mode (`-i`)

```bash
lynx-compare -p -i
```

Commands: `timeout N`, `export FILE`, `about`, `quit`.

### Full-screen TUI (`-tui`)

```bash
lynx-compare -p -tui
```

Keyboard shortcuts: `q` quit, `x` export, `F1` about.

### Graphical Interface (`-x`)

```bash
lynx-compare -p -x
```

Dark-themed GUI with collapsible section cards, threaded background
analysis, and export dialog.

### REST API Server

```bash
lynx-compare-server
lynx-compare-server --port 8080
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/compare` | GET/POST | Compare two companies |
| `/export` | GET/POST | Export comparison to file |
| `/health` | GET | Health check |
| `/about` | GET | Developer and license info |

See [docs/REST_API.md](docs/REST_API.md) for full endpoint documentation.

## Comparison Sections

| Section | Metrics | Winner Logic |
|---------|---------|--------------|
| **Valuation** | P/E, P/B, P/S, P/FCF, EV/EBITDA, EV/Revenue, PEG, ... | Lower is better (cheaper) |
| **Profitability** | ROE, ROA, ROIC, margins (gross, operating, net, FCF) | Higher is better |
| **Solvency** | D/E, D/EBITDA, current ratio, quick ratio, Altman Z, ... | Lower debt is better |
| **Growth** | Revenue/earnings CAGR 3Y/5Y, FCF growth, dilution | Higher growth is better |
| **Efficiency** | Asset/inventory/receivable turnover, DSO, DIO, CCC | Better efficiency wins |
| **Moat** | Moat score, ROIC consistency, margin stability, position | Higher/stronger is better |
| **Intrinsic Value** | DCF, Graham, NCAV, Lynch fair value, margin of safety | Higher upside is better |

The overall winner is determined by sections won (tie-broken by total
metrics won).

## Export Formats

```bash
# HTML (self-contained, styled)
lynx-compare -p AAPL MSFT --export report.html

# PDF (requires weasyprint)
pip install weasyprint
lynx-compare -p AAPL MSFT --export report.pdf

# Plain text (80-char width)
lynx-compare -p AAPL MSFT --export report.txt
```

## Python API

```python
from lynx_compare import compare_companies

view = compare_companies("AAPL", "MSFT")
print(view.summary())
print(view.overall_winner)
print(view.scoreboard())
```

See [docs/API.md](docs/API.md) for full API reference.

## Running Tests

```bash
# Install with test dependencies
pip install -e ".[test]"

# Run all 81 tests
robot tests/

# Run a specific suite
robot tests/test_engine.robot

# Save HTML report
robot --outputdir results/ tests/
```

See [docs/TESTING.md](docs/TESTING.md) for full testing guide with suite descriptions.

## CLI Reference

```
usage: lynx-compare [-h] [-p | -t] [-i | -tui | -x] [--timeout SECS]
                    [--refresh] [--no-reports] [--no-news] [--verbose]
                    [--version] [--about] [--export FILE]
                    [COMPANY ...]
```

| Flag | Description |
|------|-------------|
| `-p`, `--production-mode` | Production mode (cached data) |
| `-t`, `--testing-mode` | Testing mode (always fresh) |
| `COMPANY` | Two company identifiers (ticker, ISIN, or name) |
| `-i`, `--interactive-mode` | Interactive prompt loop |
| `-tui`, `--textual-ui` | Textual terminal UI |
| `-x`, `--gui` | Graphical interface |
| `--timeout SECS` | Timeout per company analysis (default: 30s) |
| `--refresh` | Force fresh data download |
| `--no-reports` | Skip SEC filing download |
| `--no-news` | Skip news fetching |
| `--export FILE` | Export to .html, .pdf, or .txt |
| `--about` | Show developer and license info |
| `--version` | Show version |

## Project Structure

```
lynx-compare/
  lynx_compare/               Python package
    __init__.py                Version, lazy imports
    __main__.py                Entry point
    engine.py                  Comparison logic, metric rules
    api.py                     Public API, ComparisonView
    cli.py                     Argument parsing, dispatch
    display.py                 Rich terminal output
    interactive.py             Interactive prompt mode
    export.py                  HTML/PDF/TXT export
    about.py                   Branding, license, easter egg
    server.py                  Flask REST API server
    tui/app.py                 Textual terminal UI
    gui/app.py                 Tkinter graphical interface
    img/                       Logo assets
  tests/
    *.robot                    Robot Framework test suites
    LynxCompareLibrary.py      Test keyword library
  docs/
    API.md                     Python API reference
    REST_API.md                HTTP API reference
    EXPORT.md                  Export format documentation
    ABOUT.md                   Application information
  lynx-compare.py              Entry point script
  pyproject.toml               Build configuration
```

## Documentation

- [Python API Reference](docs/API.md) -- library API with examples
- [REST API Reference](docs/REST_API.md) -- HTTP endpoints with curl examples
- [Export Formats](docs/EXPORT.md) -- HTML, PDF, and plain-text export

## Author

**Borja Tarraso** -- <borja.tarraso@member.fsf.org>

## License

[BSD 3-Clause License](LICENSE)

---

## Author and signature

This project is part of the **Lince Investor Suite**, authored and signed by

> **Borja Tarraso** &lt;[borja.tarraso@member.fsf.org](mailto:borja.tarraso@member.fsf.org)&gt;
> Licensed under BSD-3-Clause.

Every report and export emitted by Suite tools includes this same
signature in its footer. The shipped logo PNGs additionally carry the
author's signature via steganography for provenance — please do not
replace or re-encode the logo files.

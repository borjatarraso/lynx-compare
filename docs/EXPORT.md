# Lynx Compare — Export Guide

Lynx Compare can export comparison results to HTML, PDF, and plain-text formats. All exports use a **white background** with dark text for readability regardless of the application theme.

## Supported Formats

| Format | Extension | Description                              |
| ------ | --------- | ---------------------------------------- |
| HTML   | `.html`   | Styled HTML document, print-friendly     |
| PDF    | `.pdf`    | PDF via weasyprint or wkhtmltopdf        |
| Text   | `.txt`    | Plain-text with ASCII alignment (80 col) |

## Default Save Location

Exports are saved by default to `~/Documents/lynx-compare/` (or `~/lynx-compare/` if `~/Documents` doesn't exist). Filenames include tickers and a timestamp:

```
~/Documents/lynx-compare/AAPL_vs_MSFT_20260416_143022.html
```

Parent directories are created automatically if they don't exist.

## Usage by Mode

### Console Mode (CLI)

```bash
# Export to HTML (explicit path)
lynx-compare -p AAPL MSFT --export comparison.html

# Export using format keyword (auto-generates path)
lynx-compare -p AAPL MSFT --export html
lynx-compare -p AAPL MSFT --export pdf
lynx-compare -p AAPL MSFT --export text
```

### Interactive Mode

```
> export            # opens format chooser (1=HTML, 2=PDF, 3=Text)
> export html       # export with default path
> export pdf        # export with default path
> export report.html   # export to explicit path
```

### TUI Mode

Press `x` on the result screen. A dialog shows the default save path (pre-filled with tickers and timestamp). Change the extension to switch format.

### Graphical Mode

Click the **Export** button in the toolbar. A styled dialog lets you:
- Choose format via radio buttons (HTML / PDF / Text)
- See and edit the default save path
- Browse for a custom location

### Python API

```python
from lynx_compare.export import export_comparison, export_html, export_text

# Using the dispatcher
export_comparison(comparison_result, "output.html", "html")
export_comparison(comparison_result, "output.txt", "text")
export_comparison(comparison_result, "output.pdf", "pdf")

# Direct functions
html_string = export_html(comparison_result)
text_string = export_text(comparison_result)

# Default path helper
from lynx_compare.export import default_export_path
path = default_export_path(comparison_result, ".html")
```

### REST API

```
GET /export?a=AAPL&b=MSFT&format=html
GET /export?a=AAPL&b=MSFT&format=text
GET /export?a=AAPL&b=MSFT&format=pdf
```

## PDF Requirements

PDF export requires one of:

1. **weasyprint** (recommended): `pip install lynx-compare[pdf]`
2. **wkhtmltopdf**: System package (e.g., `apt install wkhtmltopdf`)

If neither is available, the HTML version is saved alongside an error message.

## Export Features

- **White background** with dark text in all formats
- **Print-friendly** CSS with `@media print` support in HTML/PDF
- **80-column alignment** in plain text using pure ASCII (no multi-byte Unicode)
- **Section headers** with winner badges
- **Warnings** displayed prominently at the top
- **Footer** with generator info, developer, and license
- **Scoreboard** and **final verdict** sections
- **Auto-creates directories** if the target path doesn't exist

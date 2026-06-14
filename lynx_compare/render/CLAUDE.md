# lynx_compare/render/ — presentation & serialization

Turns `core` result dataclasses into human-facing output. Depends on
`lynx_compare.core` (and the package version constants); nothing in `core`
depends on `render`.

## Modules & public interface

- **`display.py`** — `display_comparison(...)` renders a `ComparisonResult`
  to the terminal with `rich` (three-column A | verdict | B layout).
- **`export.py`** — file exporters, all on a white background regardless of theme:
  - `export_text(...)`, `export_html(...)`, `export_pdf(...)`
  - `export_comparison(...)` — dispatch by file extension.
  - `default_export_path(...)` (plus private `_default_export_dir`).
  - PDF export requires the optional `weasyprint` dependency (`.[pdf]`).

## Conventions

- Consume `core` dataclasses; do not re-implement comparison logic here.
- `display.py` may emit Rich markup; exported files must stay plain/printable.
- Reachable at legacy paths `lynx_compare.display` / `.export` via shims —
  edit them **here**.

# lynx_compare/interfaces/ — entry points

Wires the `core` and `render` layers to humans and API clients. Top of the
dependency chain: may import from `core`, `render`, `tui`, `gui`, and
`lynx_compare.api`.

## Modules & public interface

- **`cli.py`** — `build_parser()`, `run_cli()`, and the `AnalysisTimeoutError`
  exception. Parses arguments and dispatches to plain output, the interactive
  REPL, the TUI (`tui.app.run_tui`), the GUI (`gui.app.run_gui`), or export.
  Frontends are imported lazily inside the dispatch so optional UI deps load
  only when used. (Private helper: `_run_analysis`.)
- **`interactive.py`** — `run_interactive()`, the REPL loop for repeated
  comparisons with export/timeout commands.
- **`server.py`** — `create_app()` (Flask app factory) and `run_server()`,
  exposing `/compare`, `/compare-many`, and `/export` endpoints. Backs the
  `lynx-compare-server` console script. Requires `flask`.

## Conventions

- Keep request/dispatch glue here; comparison logic belongs in `core`,
  rendering in `render`.
- `tui` and `gui` are sibling subpackages (not under `interfaces`); `cli`
  launches them on demand — preserve the lazy imports so headless installs
  don't pay for Textual/Tkinter.
- Reachable at legacy paths `lynx_compare.cli` / `.interactive` / `.server`
  via shims (the entry points and tests use them) — edit them **here**.

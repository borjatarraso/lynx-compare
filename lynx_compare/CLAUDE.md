# lynx_compare/ — package guide

The `lynx_compare` package. Root-level modules form the public facade; the
implementation is grouped into four subpackages. See the repository-root
`CLAUDE.md` for build/test commands.

## What lives at the package root (public facade — keep paths stable)

- `__init__.py` — version constants (`__version__`, `SUITE_*`) and the curated
  public API, exposed via a lazy `__getattr__` (`compare_companies`,
  `compare_reports`, `ComparisonView`, `ComparisonResult`, `MetricResult`,
  `SectionResult`, `Warning`, `compare`).
- `__main__.py` — `main()`, the `lynx-compare` console script.
- `api.py` — the documented Python API; thin wrapper over `core.engine`.
- `plugin.py` — `register()` returning a `SectorAgent` descriptor for the
  Lince Investor Suite plugin registry.
- `engine.py`, `multi.py`, `about.py`, `display.py`, `export.py`, `cli.py`,
  `interactive.py`, `server.py` — **backward-compat shims only.** Each is a
  `sys.modules` alias to its new home under `core/`, `render/`, or
  `interfaces/`. Do not add logic here; edit the canonical module instead.

## Subpackages

| Package      | Responsibility                                   | Detail |
|--------------|--------------------------------------------------|--------|
| `core/`      | Comparison logic + metadata, no I/O              | `core/CLAUDE.md` |
| `render/`    | Rich terminal output + HTML/PDF/text export      | `render/CLAUDE.md` |
| `interfaces/`| CLI, interactive REPL, Flask REST server         | `interfaces/CLAUDE.md` |
| `tui/`       | Textual terminal UI                              | `tui/CLAUDE.md` |
| `gui/`       | Tkinter desktop UI                               | `gui/CLAUDE.md` |

Import rule: dependencies point inward (`interfaces`/`tui`/`gui` → `render` →
`core`); `core` imports only the package-level version constants and the
external `lynx-investor-core` types.

## Conventions

- Add new code to the canonical subpackage and import via its real path
  (`lynx_compare.core.engine`, `lynx_compare.render.export`, …), not the shims.
- Image assets live in `img/` and ship as package data (see `pyproject.toml`).

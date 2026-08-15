# Lynx Compare — agent guide

Side-by-side fundamental-analysis comparison tool for the Lince Investor
Suite. Takes two (or N) companies, ranks them metric-by-metric, and renders
the verdict to a terminal, a Textual TUI, a Tkinter GUI, exported files
(HTML/PDF/text), or a REST API.

## Layout

```
lynx-compare.py            Convenience launcher (python3 lynx-compare.py ...)
lynx_compare/              The package
├── __init__.py            Public API surface (lazy re-exports) + version
├── __main__.py            `lynx-compare` console entry point
├── api.py                 Documented Python API (compare_companies, ComparisonView)
├── plugin.py              Lince Investor Suite plugin registration
├── core/                  Domain logic + metadata — no I/O          → core/CLAUDE.md
├── render/                Presentation: Rich display + HTML/PDF/text → render/CLAUDE.md
├── interfaces/            CLI, REPL, Flask REST server               → interfaces/CLAUDE.md
├── tui/                   Textual terminal UI                        → tui/CLAUDE.md
└── gui/                   Tkinter desktop UI                         → gui/CLAUDE.md
tests/                     Robot Framework suites + pytest (test_multi.py)
docs/                      Hand-written reference (API, EXPORT, REST_API, TESTING, ABOUT)
```

Dependency direction is one-way: `interfaces`/`tui`/`gui` → `render` → `core`.
`core` imports nothing from the other subpackages.

## Build / run / test

```bash
pip install -e ".[test]"          # editable install with Robot Framework
lynx-compare AAPL MSFT            # CLI (also: python3 -m lynx_compare)
lynx-compare -tui AAPL MSFT       # Textual TUI    (-t/-p plain, -i interactive, -x GUI)
lynx-compare-server              # Flask REST API

robot tests/                      # Robot Framework suites (offline, mock data)
python3 -m pytest tests/          # pytest suite (N-way comparison)
```

Tests need no network — they run against mock data. Note: `tests/test_version.robot`
and one case in `tests/test_about.robot` currently assert an older version string
and fail against the live version; this predates this guide.

## Conventions for agents

- **Keep the dependency direction.** Never import `render`, `interfaces`,
  `tui`, or `gui` from `core`. New pure logic belongs in `core`.
- **Don't break the public import paths.** `lynx_compare.engine`,
  `.multi`, `.about`, `.display`, `.export`, `.cli`, `.interactive`,
  `.server` still resolve via thin re-export shims (`sys.modules` aliases)
  for backward compatibility — tests, the `pyproject.toml` entry points, and
  `docs/` rely on them. When adding code, import from the **canonical**
  subpackage path (e.g. `lynx_compare.core.engine`); leave the shims as-is.
- **The stable public API** is the curated top-level names in
  `lynx_compare/__init__.py` (`compare_companies`, `ComparisonResult`, …)
  and `lynx_compare.api`. Don't rename these.
- External domain types come from `lynx-investor-core`
  (`lynx.models.AnalysisReport`, `lynx.core.storage.set_mode`).
- Each subpackage has its own `CLAUDE.md` — read it before changing that area.

<!-- LYNX-EP-NOTE:BEGIN -->

## Entry-point card — keep it current

This project carries `index.ep.md` (and `index.ep.html`), the standard card
that answers what this is, where to look first, and how to run it. Every
project in `~/claude/` has one in the same shape, so jumping between them
does not mean re-learning where to look.

**When work here changes any of the following, refresh the card:**

- what the project is or does (title, one-line purpose, description)
- the file someone should open first
- the command that starts it
- the top-level layout or where the documentation lives

Refresh it with:

```bash
python3 ~/claude/lynx_factory/web/tools/gen_ep_index.py --only <this-project>
```

That regenerates from this repo's own README/CLAUDE.md plus the Lynx Factory
ledger — it does not invent anything, so fixing the card usually means fixing
the README first. The README's ownership footer is refreshed by the same
command.

To hand-write a card and stop it being regenerated, set `ep_locked: true` in
its front matter.

<!-- LYNX-EP-NOTE:END -->

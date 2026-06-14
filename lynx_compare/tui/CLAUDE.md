# lynx_compare/tui/ — Textual terminal UI

A full-screen terminal UI built on [Textual](https://textual.textualize.io/).
Launched lazily by `interfaces.cli` when the user passes `-tui`.

## Public interface

- **`app.py`** — `run_tui(args) -> None`, the entry point.
  - Screens/modals: `LynxCompareApp` (the `App`), `InputScreen`,
    `ResultScreen`, `AboutModal`, `EasterEggModal`, `ExportModal`,
    `TimeoutModal`.

## Conventions

- Presentation only. Comparison comes from `core` (via `compare` / `fmt_value`)
  and exports from `render.export`; do not duplicate that logic here.
- Reuses the same comparison run as the CLI through
  `interfaces.cli._run_analysis`.
- Existing code imports core/render through the legacy facade paths
  (`lynx_compare.engine`, `lynx_compare.about`, `lynx_compare.export`,
  `lynx_compare.cli`), which still resolve via shims. New imports should use
  the canonical paths (`lynx_compare.core.*`, `lynx_compare.render.*`).
- Private cell-formatting helpers (`_cell_value`, `_cell_arrow_*`,
  `_build_warnings`) are UI-local — keep them here.

# lynx_compare/gui/ — Tkinter desktop UI

A desktop GUI built on Tkinter (standard library). Launched lazily by
`interfaces.cli` when the user passes `-x`.

## Public interface

- **`app.py`** — `run_gui(args) -> None`, the entry point.
  - Windows/dialogs: `LynxCompareGUI` (main window), `SplashScreen`,
    `CollapsibleCard`, `AboutDialog`, `EasterEggDialog`, `ExportDialog`.

## Conventions

- Presentation only. Comparison comes from `core` (via `compare` / `fmt_value`)
  and exports from `render.export`; do not duplicate that logic here.
- Reuses the same comparison run as the CLI through
  `interfaces.cli._run_analysis`.
- Existing code imports core/render through the legacy facade paths
  (`lynx_compare.engine`, `lynx_compare.about`, `lynx_compare.export`,
  `lynx_compare.cli`), which still resolve via shims. New imports should use
  the canonical paths (`lynx_compare.core.*`, `lynx_compare.render.*`).
- Private layout/format helpers (`_fmt_mcap`, `_winner_fg`, `_arrow_text`,
  `_make_row`, `_styled_btn`) are UI-local — keep them here.

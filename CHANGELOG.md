# Changelog

## 6.0.0 — 2026-04-26

**Major release synchronising the entire Lince Investor Suite.**

### What's new across the Suite

- **lynx-fund** — brand-new mutual / index fund analysis tool, rejecting
  ETFs and stocks at the resolver level. Surfaces share classes, loads,
  12b-1 fees, manager tenure, persistence, capital-gains tax drag, and
  20-rule passive-investor checklist with tailored tips.
- **lynx-compare-fund** — head-to-head comparison for two mutual / index
  funds. Adds a Boglehead-style Passive-Investor Verdict, plus warnings
  for active-vs-passive, UCITS, soft- / hard-close, and distribution-
  policy mismatches.
- **lynx-theme** — visual theme editor for the entire Suite (GUI + TUI
  only). Edit colours, fonts, alignment, bold / italic / underline /
  blink / marquee for 15 styled areas with live preview. Three built-in
  read-only reference themes (`lynx-mocha`, `lynx-latte`,
  `lynx-high-contrast`). Sets the default theme persisted to
  `$XDG_CONFIG_HOME/lynx-theme/default.json`.
- **i18n** — every Suite CLI now accepts `--language=us|es|it|de|fr|fa`
  and persists the user's choice to `$XDG_CONFIG_HOME/lynx/language.json`.
  GUI apps mount a small bottom-right language toggle (left-click
  cycles, right-click opens a chooser); TUI apps bind `g` to cycle.
  Honours `LYNX_LANG` for ad-hoc shells.
- **Author signature footer** — every txt / html / pdf export now ends
  with the Suite-wide author block: *Borja Tarraso
  &lt;borja.tarraso@member.fsf.org&gt;*. Provided by the new
  `lynx_investor_core.author_footer` module.

### Dashboard

- Two new APP launchables (Lynx Fund, Lynx Compare Fund, Lynx Theme),
  raising the catalogue to **8 apps + 11 sector agents = 19
  launchables**.
- Per-app launch dialect (`run_mode_dialect`, `ui_mode_flags`,
  `accepts_identifier`) so the launcher emits argv each app
  understands; lynx-theme + lynx-portfolio launch correctly from every
  mode.
- `--recommend` now rejects empty queries instead of silently passing.

### Bug fixes

- `__main__.py` of every fund / compare-fund / etf / compare-etf entry
  point now propagates `run_cli`'s return code so non-zero exits are
  visible to shell scripts and CI pipelines.
- Stale-install hygiene: pyproject editable installs now overwrite
  cached site-packages copies cleanly.
- Cosmetic clean-up: remaining "ETF" labels in fund / compare-fund
  GUI / TUI / interactive prompts → "Fund".
- Validation: empty positional ticker, missing second comparison
  ticker, and `--recommend ""` now exit non-zero with a clear message.


## [4.0] - 2026-04-23

Part of **Lince Investor Suite v4.0** coordinated release.

### Added
- Dedicated ticker / identifier validator on every HTTP endpoint of the
  compare server — blocks CR/LF / semicolon injection into
  `Content-Disposition` filenames.

### Changed
- Server no longer echoes upstream exception text; errors are logged
  server-side and returned as generic "comparison failed" / "export
  failed" messages.
- `--timeout` must be >= 5 seconds.
- Depends on `lynx-investor-core>=4.0`.

All notable changes to **Lynx Compare** are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [3.0] - 2026-04-22

Part of **Lince Investor Suite v3.0** coordinated release.

### Added
- Uniform PageUp / PageDown navigation across every UI mode (GUI, TUI,
  interactive, console). Scrolling never goes above the current output
  in interactive and console mode; Shift+PageUp / Shift+PageDown remain
  reserved for the terminal emulator's own scrollback.

### Changed
- TUI wires `lynx_investor_core.pager.PagingAppMixin` and
  `tui_paging_bindings()` into the main application.
- Graphical mode binds `<Prior>` / `<Next>` / `<Control-Home>` /
  `<Control-End>` via `bind_tk_paging()`.
- Interactive mode pages long output through `console_pager()` /
  `paged_print()`.
- New dependency on `lynx-investor-core>=2.0` for the shared pager module.

---

## [v2.0] — 2026-04-19

Major release — **Lince Investor Suite v2.0** unified release.

### Changed
- **Unified suite**: All Lince Investor projects now share consistent
  version numbering, logos, keybindings, CLI patterns, export styling,
  installation instructions, and documentation structure.
- **Version format**: Now `2.0` (was `1.0.0`) to match the rest of the
  suite's two-part versioning scheme.
- **TUI keybindings**: Standardized to `F1` (About), `q` (Quit),
  `x` (Export), `t` (Timeout) to match the rest of the suite (was
  `Ctrl+A`, `Ctrl+Q`, `Ctrl+E`, `Ctrl+T`).
- **Documentation**: Updated all docs to reflect v2.0 and unified
  keybindings.

---

## [v1.0] — 2026-04-15

First production-stable major release.

- Side-by-side fundamental analysis comparison across 7 sections
- 40+ metrics with directional rules (higher/lower is better)
- Four interfaces: CLI, Interactive, TUI, GUI
- REST API server via Flask
- Export formats: HTML, PDF, TXT
- Public Python API
- Comparability warnings for sector/industry/tier mismatches
- BSD 3-Clause License

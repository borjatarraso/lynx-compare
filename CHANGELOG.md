# Changelog

All notable changes to **Lynx Compare** are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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

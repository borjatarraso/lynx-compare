---
ep_version: 1
project: lynx-compare
title: Lynx Compare
status: PAUSED
last_touched: 2026-06-15
last_touched_text: 15 June 2026
section: sub
category: investments
generated: 2026-08-15
ep_locked: false   # set true and this file is never regenerated
---

# Lynx Compare

> Compare stocks from fundamentals

🟠 **PAUSED** · last touched **15 June 2026** (last commit)

---

## What this is

**Side-by-side fundamental analysis comparison tool**

Lynx Compare is part of the **Lince Investor** suite. It compares two publicly traded companies across seven fundamental analysis sections: valuation, profitability, solvency, growth, efficiency, moat, and intrinsic value.

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

All dependencies are installed automatically via `pip install -e .`.

Displays a three-column comparison with unicode arrows showing the winner for each metric, color-coded section verdicts, and an overall winner.

Commands: `timeout N`, `export FILE`, `about`, `quit`.

Keyboard shortcuts: `q` quit, `x` export, `F1` about.

Dark-themed GUI with collapsible section cards, threaded background analysis, and export dialog.

See [docs/REST_API.md](docs/REST_API.md) for full endpoint documentation.

The overall winner is determined by sections won (tie-broken by total metrics won).

view = compare_companies("AAPL", "MSFT") print(view.summary()) print(view.overall_winner) print(view.scoreboard()) ```

See [docs/API.md](docs/API.md) for full API reference.

See [docs/TESTING.md](docs/TESTING.md) for full testing guide with suite descriptions.

- [Python API Reference](docs/API.md) -- library API with examples
- [REST API Reference](docs/REST_API.md) -- HTTP endpoints with curl examples
- [Export Formats](docs/EXPORT.md) -- HTML, PDF, and plain-text export

**Borja Tarraso** -- <borja.tarraso@member.fsf.org>

[BSD 3-Clause License](LICENSE)

This project is part of the **Lince Investor Suite**, authored and signed by

**Borja Tarraso** &lt;[borja.tarraso@member.fsf.org](mailto:borja.tarraso@member.fsf.org)&gt; Licensed under BSD-3-Clause.

Every report and export emitted by Suite tools includes this same signature in its footer. The shipped logo PNGs additionally carry the author's signature via steganography for provenance — please do not replace or re-encode the logo files.

<!-- LYNX-EP-FOOTER:BEGIN -->

New here, or coming back after a while? Read [`index.ep.md`](index.ep.md) (or open [`index.ep.html`](index.ep.html) in a browser) — the standard card that answers what this is, where to look first, and how to run it, in the same shape for every project.

🟠 **PAUSED** · last touched **15 June 2026**

<img src="https://www.cortex-university.com/static/brand/lince-logo.png" alt="Lince" width="96" height="96" align="left" style="margin-right:16px" />

**Lynx Compare is proudly part of Lince.**

Part of the LINCE company · © All rights reserved

<!-- LYNX-EP-FOOTER:END -->

## Start here

- [`README.md`](README.md) — what the project is, in its own words
- [`CLAUDE.md`](CLAUDE.md) — working agreement for a session in this repo

## Run it

```bash
cd ~/claude/lince-investor/lynx-compare
lynx-compare                          # console entry point
lynx-compare-server                   # console entry point
python3 -m lynx_compare               # runnable package
```

## The rest of it

**Directories**

- `docs/` — 5 entries
- `lynx_compare/` — 20 entries
- `lynx_compare.egg-info/` — 6 entries
- `tests/` — 12 entries

**Other documentation**

- [`CHANGELOG.md`](CHANGELOG.md)

**`docs/`** holds 5 files.

**Build / config**: `pyproject.toml`

---

## Ownership

<img src="https://www.cortex-university.com/static/brand/lince-logo.png" alt="Lince" width="96" height="96" align="left" style="margin-right:16px" />

**Lynx Compare is proudly part of Lince.**

| Company ID | Headquarters |
|---|---|
| 3015071-2 | Helsinki, Finland |

Part of the LINCE company · © All rights reserved


<sub>Standard entry-point card (`index.ep.md`, format v1) — generated 2026-08-15 by Lynx Factory. Regenerating overwrites this file unless `ep_locked: true`.</sub>

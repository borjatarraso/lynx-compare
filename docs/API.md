# Lynx Compare v2.0 — Python API Reference

Lynx Compare can be used as a Python library in addition to the CLI. This document covers the public API.

## Quick Example

```python
from lynx.core.storage import set_mode
set_mode("production")  # IMPORTANT: always set mode before any data operations

from lynx_compare import compare_companies

result = compare_companies("AAPL", "MSFT")

print(result.winner_ticker)            # "MSFT"
print(result.summary())               # "MSFT wins 6-1 sections (30-15 metrics) vs AAPL"
print(result.section_winner("Moat"))   # "b"
print(result.metric_winner("roic"))    # "a"
```

---

## High-Level API

### `compare_companies(identifier_a, identifier_b, ...) -> ComparisonView`

Main entry point. Resolves identifiers via lynx-fa, runs fundamental analysis for both companies, and returns the comparison.

```python
from lynx_compare import compare_companies

result = compare_companies(
    identifier_a="AAPL",        # Ticker, ISIN, or company name
    identifier_b="MSFT",        # Ticker, ISIN, or company name
    refresh=False,              # True = ignore cache, re-fetch from network
    download_reports=False,     # Fetch SEC filings during analysis
    download_news=False,        # Fetch news articles during analysis
    verbose=False,              # Enable verbose output from lynx-fa
)
```

**Returns:** `ComparisonView`

**Raises:** `ValueError` if either identifier cannot be resolved.

---

### `compare_reports(report_a, report_b) -> ComparisonView`

Compare two pre-built `AnalysisReport` objects. Use this when you already have the reports and want to skip the resolution/fetch step.

```python
from lynx.core.storage import set_mode
from lynx.core.analyzer import run_full_analysis
from lynx_compare import compare_reports

set_mode("production")
a = run_full_analysis("AAPL")
b = run_full_analysis("MSFT")

result = compare_reports(a, b)
```

**Returns:** `ComparisonView`

---

## ComparisonView

The `ComparisonView` is a read-only wrapper over `ComparisonResult` with convenience methods for querying results.

### Identity Properties

| Property | Type | Description |
|----------|------|-------------|
| `ticker_a` | `str` | Ticker of the first company |
| `ticker_b` | `str` | Ticker of the second company |
| `name_a` | `str` | Full name of the first company |
| `name_b` | `str` | Full name of the second company |

### Overall Winner

| Property / Method | Type | Description |
|-------------------|------|-------------|
| `overall_winner` | `str` | `"a"`, `"b"`, or `"tie"` |
| `winner_ticker` | `str \| None` | Ticker of the winner, `None` on tie |
| `winner_name` | `str \| None` | Company name of the winner, `None` on tie |

```python
result = compare_companies("AAPL", "MSFT")

result.overall_winner   # "b"
result.winner_ticker    # "MSFT"
result.winner_name      # "Microsoft Corporation"
```

### Score Tallies

| Property | Type | Description |
|----------|------|-------------|
| `sections_won_a` | `int` | Number of sections won by company A |
| `sections_won_b` | `int` | Number of sections won by company B |
| `total_wins_a` | `int` | Total metric wins for company A |
| `total_wins_b` | `int` | Total metric wins for company B |
| `total_ties` | `int` | Total metrics that tied |

```python
result.sections_won_a  # 1
result.sections_won_b  # 6
result.total_wins_a    # 15
result.total_wins_b    # 30
result.total_ties      # 3
```

### Warnings

| Property | Type | Description |
|----------|------|-------------|
| `warnings` | `list[Warning]` | Comparability warnings |
| `has_warnings` | `bool` | `True` if any warnings exist |

Each `Warning` has:
- `level`: `"sector"` (most severe), `"industry"`, or `"tier"` (least severe)
- `message`: Human-readable description

```python
result = compare_companies("AAPL", "GOOG")

for w in result.warnings:
    print(f"[{w.level.upper()}] {w.message}")
# [SECTOR] Different sectors: AAPL is in Technology, GOOG is in Communication Services...
```

### Section Access

#### `section_names -> list[str]`

Ordered list of all section names.

```python
result.section_names
# ['Valuation', 'Profitability', 'Solvency', 'Growth',
#  'Efficiency', 'Moat', 'Intrinsic Value']
```

#### `section(name) -> SectionResult`

Get a section by name (case-insensitive). Raises `KeyError` if not found.

```python
s = result.section("Valuation")
s.name       # "Valuation"
s.winner     # "b"
s.wins_a     # 2
s.wins_b     # 7
s.ties       # 0
s.metrics    # list[MetricResult] — all metrics in this section
```

#### `section_winner(name) -> str`

Winner of a named section: `"a"`, `"b"`, or `"tie"`.

```python
result.section_winner("Profitability")  # "b"
result.section_winner("Efficiency")     # "a"
```

#### `section_winner_ticker(name) -> str | None`

Ticker of the section winner, or `None` on tie.

```python
result.section_winner_ticker("Moat")  # "MSFT"
```

#### `sections_won_by(ticker) -> list[SectionResult]`

Return all sections won by the given ticker.

```python
for s in result.sections_won_by("AAPL"):
    print(s.name)  # "Efficiency"
```

### Metric Access

#### `metric(key) -> MetricResult`

Look up a single metric by its key. Raises `KeyError` if not found.

```python
m = result.metric("pe_trailing")
m.key       # "pe_trailing"
m.label     # "P/E (Trailing)"
m.value_a   # 33.01
m.value_b   # 23.21
m.winner    # "b"   (lower P/E wins)
m.fmt_a     # "33.01"
m.fmt_b     # "23.21"
```

#### `metric_winner(key) -> str`

Winner for a specific metric: `"a"`, `"b"`, `"tie"`, or `"na"`.

```python
result.metric_winner("roic")           # "a"
result.metric_winner("gross_margin")   # "b"
result.metric_winner("peg_ratio")      # "na"  (both N/A)
```

#### `metric_winner_ticker(key) -> str | None`

Ticker of the metric winner, or `None` on tie/na.

```python
result.metric_winner_ticker("moat_score")  # "MSFT"
```

#### `metrics_won_by(ticker) -> list[MetricResult]`

Return all metrics won by the given ticker.

```python
for m in result.metrics_won_by("AAPL"):
    print(f"{m.label}: {m.fmt_a} vs {m.fmt_b}")
# Return on Equity: 152.02% vs 34.39%
# Return on Assets: 24.38% vs 14.86%
# ...
```

### Serialisation

#### `summary() -> str`

One-line human-readable summary.

```python
result.summary()
# "MSFT wins 6-1 sections (30-15 metrics) vs AAPL"
```

#### `to_dict() -> dict`

Serialise the full comparison to a plain dict. JSON-serialisable.

```python
import json
data = result.to_dict()
print(json.dumps(data, indent=2))
```

#### `scoreboard() -> dict[str, dict]`

Section-by-section scoreboard as a dict.

```python
for name, info in result.scoreboard().items():
    wt = info["winner_ticker"] or "TIE"
    print(f"  {name:20s}  {info['wins_a']}W-{info['wins_b']}W  -> {wt}")

#   Valuation             2W-7W  -> MSFT
#   Profitability         3W-5W  -> MSFT
#   Solvency              6W-8W  -> MSFT
#   Growth                3W-4W  -> MSFT
#   Efficiency            1W-0W  -> AAPL
#   Moat                  0W-3W  -> MSFT
#   Intrinsic Value       0W-3W  -> MSFT
```

---

## Low-Level Data Structures

These are plain `dataclass` objects used by the engine. You can import them directly if you need more control.

### `ComparisonResult`

The raw comparison result. `ComparisonView.raw` gives you access to this.

```python
from lynx_compare import ComparisonResult

@dataclass
class ComparisonResult:
    ticker_a: str
    ticker_b: str
    name_a: str
    name_b: str
    tier_a: str                          # e.g. "Mega Cap"
    tier_b: str
    sector_a: str
    sector_b: str
    industry_a: str
    industry_b: str
    market_cap_a: float | None
    market_cap_b: float | None
    sections: list[SectionResult]
    warnings: list[Warning]
    total_wins_a: int
    total_wins_b: int
    total_ties: int
    sections_won_a: int
    sections_won_b: int
    sections_tied: int
    overall_winner: str                  # "a", "b", or "tie"
```

### `SectionResult`

```python
from lynx_compare import SectionResult

@dataclass
class SectionResult:
    name: str                            # e.g. "Valuation"
    metrics: list[MetricResult]
    wins_a: int
    wins_b: int
    ties: int
    winner: str                          # "a", "b", or "tie"
```

### `MetricResult`

```python
from lynx_compare import MetricResult

@dataclass
class MetricResult:
    key: str          # e.g. "pe_trailing"
    label: str        # e.g. "P/E (Trailing)"
    value_a: object   # raw value (float, str, or None)
    value_b: object
    winner: str       # "a", "b", "tie", or "na"
    fmt_a: str        # formatted display string, e.g. "33.01"
    fmt_b: str
```

### `Warning`

```python
from lynx_compare import Warning

@dataclass
class Warning:
    level: str      # "sector", "industry", or "tier"
    message: str    # human-readable description
```

### `compare(report_a, report_b) -> ComparisonResult`

Low-level comparison function. Takes two `AnalysisReport` objects and returns a raw `ComparisonResult` (no wrapper). This is what `compare_reports` calls internally.

```python
from lynx_compare import compare
from lynx.core.analyzer import run_full_analysis

a = run_full_analysis("AAPL")
b = run_full_analysis("MSFT")
raw = compare(a, b)  # ComparisonResult
```

---

## Metric Keys Reference

All metric keys that can be used with `metric()` and `metric_winner()`:

### Valuation
`pe_trailing`, `pe_forward`, `pb_ratio`, `ps_ratio`, `p_fcf`, `ev_ebitda`, `ev_revenue`, `peg_ratio`, `dividend_yield`, `earnings_yield`, `price_to_tangible_book`, `price_to_ncav`

### Profitability
`roe`, `roa`, `roic`, `gross_margin`, `operating_margin`, `net_margin`, `fcf_margin`, `ebitda_margin`

### Solvency
`debt_to_equity`, `debt_to_ebitda`, `current_ratio`, `quick_ratio`, `interest_coverage`, `altman_z_score`, `net_debt`, `total_debt`, `total_cash`, `cash_burn_rate`, `cash_runway_years`, `working_capital`, `cash_per_share`, `tangible_book_value`, `ncav`, `ncav_per_share`

### Growth
`revenue_growth_yoy`, `revenue_cagr_3y`, `revenue_cagr_5y`, `earnings_growth_yoy`, `earnings_cagr_3y`, `earnings_cagr_5y`, `fcf_growth_yoy`, `book_value_growth_yoy`, `dividend_growth_5y`, `shares_growth_yoy`

### Efficiency
`asset_turnover`, `inventory_turnover`, `receivables_turnover`, `days_sales_outstanding`, `days_inventory`, `cash_conversion_cycle`

### Moat
`moat_score`, `roic_consistency`, `margin_stability`, `revenue_predictability`, `competitive_position`, `switching_costs`, `network_effects`, `cost_advantages`, `intangible_assets`, `efficient_scale`, `niche_position`, `insider_alignment`, `asset_backing`

### Intrinsic Value
`dcf_value`, `graham_number`, `ncav_value`, `lynch_fair_value`, `asset_based_value`, `current_price`, `margin_of_safety_dcf`, `margin_of_safety_graham`, `margin_of_safety_ncav`, `margin_of_safety_asset`, `primary_method`, `secondary_method`

> **Note:** Metrics in the "informational only" set (`dcf_value`, `graham_number`, `ncav_value`, `lynch_fair_value`, `asset_based_value`, `current_price`, `primary_method`, `secondary_method`, and several descriptive moat fields) always return `"na"` for `winner` because they are not directly comparable without context.

---

## Winner Semantics

The `winner` field uses these values:

| Value | Meaning |
|-------|---------|
| `"a"` | First company wins this metric/section/overall |
| `"b"` | Second company wins |
| `"tie"` | Both companies have equal values |
| `"na"` | Not applicable — both values are missing, or the metric is informational only |

### Comparison Direction

Each metric has a defined comparison direction:

- **Higher is better:** ROE, margins, growth rates, moat score, cash, coverage ratios
- **Lower is better:** P/E, P/B, debt ratios, days outstanding, dilution
- **Lower positive:** P/E, P/FCF — lower wins, but negative values are penalised
- **Ordinal:** Qualitative moat fields compared by rank (e.g. Wide > Narrow > Weak)

### Winner Determination

1. **Per metric:** Determined by the comparison direction rules above
2. **Per section:** Whichever company wins more metrics in the section
3. **Overall:** Whichever company wins more sections; tied sections broken by total metric wins

---

## Export API

The `lynx_compare.export` module provides export functionality.

```python
from lynx_compare.export import export_html, export_text, export_comparison, default_export_path

# Generate HTML/text strings
html = export_html(comparison_result)
text = export_text(comparison_result)

# Write to file (format detected from extension or explicit)
path = export_comparison(comparison_result, "output.html", "html")
path = export_comparison(comparison_result, "output.txt", "text")

# Default path helper
path = default_export_path(comparison_result, ".html")
# -> ~/Documents/lynx-compare/AAPL_vs_MSFT_20260416_143022.html
```

---

## About API

The `lynx_compare.about` module provides app metadata.

```python
from lynx_compare.about import (
    APP_NAME,          # "Lynx Compare"
    DEVELOPER,         # "Borja Tarraso"
    DEVELOPER_EMAIL,   # "borja.tarraso@member.fsf.org"
    LICENSE_NAME,      # "BSD 3-Clause License"
    about_text,        # full about string
    about_lines,       # about as list of lines
    check_easter_egg,  # True if input matches trigger
    easter_egg_text,   # ASCII art
)
```

---

## Warnings

Comparability warnings are generated automatically when comparing companies with different sectors, industries, or market cap tiers. All three are independent and non-exclusive.

| Level | Severity | Condition |
|-------|----------|-----------|
| `sector` | High (red) | Different sectors |
| `industry` | Medium (orange) | Different industries |
| `tier` | Low (yellow) | Different market cap tiers |

```python
result = compare_companies("AAPL", "OCO.V")

for w in result.warnings:
    print(f"[{w.level}] {w.message}")
# [sector] Sector mismatch: AAPL (Technology) vs OCO.V (Basic Materials)
# [industry] Industry mismatch: AAPL (Consumer Electronics) vs OCO.V (Other Industrial Metals & Mining)
# [tier] Tier mismatch: AAPL (Mega Cap) vs OCO.V (Micro Cap)
```

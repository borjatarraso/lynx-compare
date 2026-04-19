# Lynx Compare v1.0 — Testing Guide

Lynx Compare uses [Robot Framework](https://robotframework.org/) for automated testing. All tests run offline using mock data — no network connection or live market data is needed.

## Prerequisites

```bash
# Install with test dependencies
pip install -e ".[test]"

# Or install Robot Framework separately
pip install robotframework
```

## Running Tests

### Run all tests

```bash
robot tests/
```

### Run a specific test suite

```bash
robot tests/test_engine.robot
robot tests/test_warnings.robot
```

### Run a specific test case

```bash
robot --test "View Has Winner Ticker" tests/test_comparison_view.robot
```

### Save results to a directory

```bash
robot --outputdir results/ tests/
```

This generates three files:
- `output.xml` — machine-readable results
- `log.html` — detailed execution log
- `report.html` — summary report (open in browser)

### Filter by tag or name pattern

```bash
# Run all tests with "export" in the suite name
robot --suite "*export*" tests/

# Run tests matching a pattern
robot --test "*Warning*" tests/
```

## Test Suites

| Suite | File | Tests | Description |
|-------|------|------:|-------------|
| About | `test_about.robot` | 6 | Developer info, license, version, CLI flag |
| API Server | `test_api.robot` | 6 | Flask endpoints, error handling |
| ComparisonView | `test_comparison_view.robot` | 14 | Python API wrapper methods |
| Engine | `test_engine.robot` | 11 | Core comparison logic, formatting |
| Export | `test_export.robot` | 13 | HTML/text generation, file output |
| Export Advanced | `test_export_advanced.robot` | 11 | Paths, alignment, edge cases |
| Modules | `test_modules.robot` | 8 | Module imports, easter egg |
| Version | `test_version.robot` | 4 | Version consistency |
| Warnings | `test_warnings.robot` | 8 | Sector/industry/tier warnings |
| **Total** | | **81** | |

## Test Architecture

### Keyword Library

All Python-side test logic lives in `tests/LynxCompareLibrary.py`. This module provides keywords that `.robot` files call to interact with Lynx Compare modules.

Key features:
- **Mock data builder** (`_build_mock_comparison_result`) — creates a realistic `ComparisonResult` with 7 sections, metrics, and warnings, without any network calls
- **Module keywords** — thin wrappers around `lynx_compare` functions
- **API client** — creates a Flask test client for REST endpoint testing

### Mock Data

Tests use a pre-built `ComparisonResult` that simulates a comparison between AAPL and MSFT with:
- 7 sections with varying winners (a, b, tie)
- 12 valuation metrics with realistic values
- Industry and sector mismatch warnings
- Consistent win tallies

This avoids any dependency on live data, yfinance, or network access.

### Adding New Tests

1. **Add a keyword** in `tests/LynxCompareLibrary.py`:
   ```python
   def my_new_keyword(arg: str) -> str:
       from lynx_compare.some_module import some_function
       return some_function(arg)
   ```

2. **Write a test case** in a `.robot` file:
   ```robot
   *** Settings ***
   Library    ../tests/LynxCompareLibrary.py

   *** Test Cases ***
   My New Test
       [Documentation]    Describe what this verifies.
       ${result}=    My New Keyword    some_value
       Should Be Equal    ${result}    expected_value
   ```

3. **Run it**:
   ```bash
   robot tests/my_new_test.robot
   ```

## What Each Suite Tests

### test_engine.robot
Validates the core comparison engine:
- `ComparisonResult` has all required fields
- Exactly 7 sections with correct names
- Winners are valid (`a`, `b`, `tie`, `na`)
- Win tallies are consistent across sections
- `fmt_value()` formats percentages, money, and None correctly
- Warnings generated for sector mismatches

### test_comparison_view.robot
Validates the `ComparisonView` API wrapper:
- `winner_ticker` and `winner_name` properties
- `summary()` returns descriptive text
- `section_names` returns all 7 sections
- `section_winner()` and `section_winner_ticker()`
- `metric_winner()` and `metric_winner_ticker()`
- `has_warnings`, `to_dict()`, `scoreboard()`
- `metrics_won_by()` and `sections_won_by()`
- `repr()` includes both tickers

### test_warnings.robot
Validates the comparability warning system:
- Industry and sector warnings present in mock data
- All three warning types fire independently (non-exclusive)
- Tier warning works standalone
- Warning levels and messages are valid
- Warnings appear in text and HTML exports

### test_api.robot
Validates REST API endpoints:
- Flask app creation
- `GET /` returns endpoints list
- `GET /health` returns ok status
- `GET /about` returns developer metadata
- `GET /compare` without params returns 400
- `GET /export` without params returns 400

### test_export.robot
Validates export output content:
- Text export contains header, company names, sections, verdict, footer
- HTML export has DOCTYPE, white background, company info, sections, styling, print CSS
- File dispatcher writes HTML and text files correctly

### test_export_advanced.robot
Validates export edge cases:
- Default export directory exists
- Default paths contain tickers, timestamps, correct extensions
- Export auto-creates nested directories
- Text lines fit within 80 characters
- Separator lines have consistent width
- Text uses ASCII only (no multi-byte Unicode)
- Bad format returns API error

### test_about.robot
Validates about/metadata:
- About text includes developer name, email, license
- About text includes version string
- `about_lines()` returns a list
- Developer metadata constants match
- `--about` CLI flag works

### test_version.robot
Validates version consistency:
- Version is `1.0`
- App name is `Lynx Compare`
- `--version` flag prints version cleanly
- `--about` flag shows current version

### test_modules.robot
Validates structural integrity:
- GUI, TUI, API, Export modules import without errors
- Easter egg endpoint returns ASCII art with lynx
- Easter egg triggers match known words
- Easter egg rejects non-trigger input
- Easter egg handles whitespace trimming

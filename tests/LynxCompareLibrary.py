"""Robot Framework keyword library for Lynx Compare tests.

Provides Python keywords that the .robot test suites call to interact
with the Lynx Compare modules without needing a live data connection.
"""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any

# ---------------------------------------------------------------------------
# Mock data  (used by tests that need a ComparisonResult without live data)
# ---------------------------------------------------------------------------

def _build_mock_comparison_result():
    """Build a realistic ComparisonResult using the engine dataclasses."""
    from lynx_compare.engine import (
        ComparisonResult, SectionResult, MetricResult, Warning,
    )

    sections = []

    # Valuation section (A wins)
    valuation = SectionResult(name="Valuation")
    val_metrics = [
        ("pe_trailing", "P/E (Trailing)", 25.3, 32.1, "a"),
        ("pe_forward", "P/E (Forward)", 22.0, 28.5, "a"),
        ("pb_ratio", "P/B Ratio", 8.1, 12.3, "a"),
        ("ps_ratio", "P/S Ratio", 5.2, 9.1, "a"),
        ("p_fcf", "P/FCF", 20.0, 30.0, "a"),
        ("ev_ebitda", "EV/EBITDA", 18.0, 22.0, "a"),
        ("ev_revenue", "EV/Revenue", 6.5, 10.2, "a"),
        ("peg_ratio", "PEG Ratio", 1.2, 2.1, "a"),
        ("dividend_yield", "Dividend Yield", 0.006, 0.008, "b"),
        ("earnings_yield", "Earnings Yield", 0.04, 0.031, "a"),
        ("price_to_tangible_book", "P/Tangible Book", 30.0, 45.0, "a"),
        ("price_to_ncav", "Price/NCAV", None, None, "na"),
    ]
    for key, label, va, vb, winner in val_metrics:
        from lynx_compare.engine import fmt_value
        valuation.metrics.append(MetricResult(
            key=key, label=label, value_a=va, value_b=vb, winner=winner,
            fmt_a=fmt_value(key, va), fmt_b=fmt_value(key, vb),
        ))
        if winner == "a":
            valuation.wins_a += 1
        elif winner == "b":
            valuation.wins_b += 1
        elif winner == "tie":
            valuation.ties += 1
    valuation.winner = "a"
    sections.append(valuation)

    # Simplified remaining sections
    for name, winner_side, wa, wb in [
        ("Profitability", "b", 2, 5),
        ("Solvency", "a", 8, 4),
        ("Growth", "b", 3, 5),
        ("Efficiency", "a", 4, 2),
        ("Moat", "tie", 3, 3),
        ("Intrinsic Value", "a", 3, 1),
    ]:
        s = SectionResult(name=name, wins_a=wa, wins_b=wb, winner=winner_side)
        s.metrics.append(MetricResult(
            key="stub", label=f"{name} stub", value_a=1.0, value_b=2.0,
            winner=winner_side, fmt_a="1.00", fmt_b="2.00",
        ))
        sections.append(s)

    total_a = sum(s.wins_a for s in sections)
    total_b = sum(s.wins_b for s in sections)
    sw_a = sum(1 for s in sections if s.winner == "a")
    sw_b = sum(1 for s in sections if s.winner == "b")
    st = sum(1 for s in sections if s.winner == "tie")

    cr = ComparisonResult(
        ticker_a="AAPL",
        ticker_b="MSFT",
        name_a="Apple Inc.",
        name_b="Microsoft Corporation",
        tier_a="Large Cap",
        tier_b="Large Cap",
        sector_a="Technology",
        sector_b="Technology",
        industry_a="Consumer Electronics",
        industry_b="Software - Infrastructure",
        market_cap_a=2_800_000_000_000,
        market_cap_b=3_100_000_000_000,
        sections=sections,
        total_wins_a=total_a,
        total_wins_b=total_b,
        sections_won_a=sw_a,
        sections_won_b=sw_b,
        sections_tied=st,
        overall_winner="a" if sw_a > sw_b else ("b" if sw_b > sw_a else "tie"),
        warnings=[
            Warning(level="industry", message="Industry mismatch: AAPL (Consumer Electronics) vs MSFT (Software - Infrastructure)"),
            Warning(level="sector", message="Sector mismatch (for testing purposes)"),
        ],
    )
    return cr


# ---------------------------------------------------------------------------
# About keywords
# ---------------------------------------------------------------------------

def get_about_text() -> str:
    from lynx_compare.about import about_text
    return about_text()


def get_about_lines() -> list[str]:
    from lynx_compare.about import about_lines
    return about_lines()


def get_developer_name() -> str:
    from lynx_compare.about import DEVELOPER
    return DEVELOPER


def get_developer_email() -> str:
    from lynx_compare.about import DEVELOPER_EMAIL
    return DEVELOPER_EMAIL


def get_license_name() -> str:
    from lynx_compare.about import LICENSE_NAME
    return LICENSE_NAME


# ---------------------------------------------------------------------------
# Easter egg keywords
# ---------------------------------------------------------------------------

def check_easter_egg(text: str) -> bool:
    from lynx_compare.about import check_easter_egg
    return check_easter_egg(text)


def get_easter_egg_text() -> str:
    from lynx_compare.about import easter_egg_text
    return easter_egg_text()


# ---------------------------------------------------------------------------
# Engine keywords
# ---------------------------------------------------------------------------

def get_mock_comparison_result():
    return _build_mock_comparison_result()


def get_section_names() -> list[str]:
    cr = _build_mock_comparison_result()
    return [s.name for s in cr.sections]


def sum_section_wins_a(cr) -> int:
    return sum(s.wins_a for s in cr.sections)


def sum_section_wins_b(cr) -> int:
    return sum(s.wins_b for s in cr.sections)


def format_value(key: str, val) -> str:
    from lynx_compare.engine import fmt_value
    return fmt_value(key, val)


def has_warning_level(cr, level: str) -> bool:
    return any(w.level == level for w in cr.warnings)


# ---------------------------------------------------------------------------
# Export keywords
# ---------------------------------------------------------------------------

def export_comparison_text() -> str:
    from lynx_compare.export import export_text
    cr = _build_mock_comparison_result()
    return export_text(cr)


def export_comparison_html() -> str:
    from lynx_compare.export import export_html
    cr = _build_mock_comparison_result()
    return export_html(cr)


def export_comparison_to_file(fmt: str) -> str:
    from lynx_compare.export import export_comparison
    cr = _build_mock_comparison_result()
    suffix = {"html": ".html", "text": ".txt", "pdf": ".pdf"}.get(fmt, ".html")
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    try:
        return export_comparison(cr, path, fmt)
    except RuntimeError:
        # PDF fallback writes HTML
        html_path = path.replace(suffix, ".html")
        if os.path.exists(html_path):
            return html_path
        raise


# ---------------------------------------------------------------------------
# API server keywords
# ---------------------------------------------------------------------------

def create_api_app() -> bool:
    """Verify the Flask app can be created."""
    try:
        from lynx_compare.server import create_app
        app = create_app(run_mode="testing")
        return app is not None
    except ImportError:
        # Flask not installed
        return False


def _get_test_client():
    from lynx_compare.server import create_app
    app = create_app(run_mode="testing")
    app.config["TESTING"] = True
    return app.test_client()


def api_get_index() -> dict:
    client = _get_test_client()
    response = client.get("/")
    return json.loads(response.data)


def api_get_health() -> dict:
    client = _get_test_client()
    response = client.get("/health")
    return json.loads(response.data)


def api_get_about() -> dict:
    client = _get_test_client()
    response = client.get("/about")
    return json.loads(response.data)


def api_get_easter_egg() -> str:
    client = _get_test_client()
    response = client.get("/easter-egg")
    return response.data.decode("utf-8")


def api_get_compare_missing() -> tuple[int, dict]:
    client = _get_test_client()
    response = client.get("/compare")
    return response.status_code, json.loads(response.data)


def api_get_export_missing() -> tuple[int, dict]:
    client = _get_test_client()
    response = client.get("/export")
    return response.status_code, json.loads(response.data)


def api_get_export_bad_format() -> tuple[int, dict]:
    client = _get_test_client()
    response = client.get("/export?a=AAPL&b=MSFT&format=xyz")
    return response.status_code, json.loads(response.data)


# ---------------------------------------------------------------------------
# Export default path keywords
# ---------------------------------------------------------------------------

def get_default_export_dir() -> str:
    from lynx_compare.export import _default_export_dir
    return str(_default_export_dir())


def get_default_export_path_html() -> str:
    from lynx_compare.export import default_export_path
    cr = _build_mock_comparison_result()
    return default_export_path(cr, ".html")


def get_default_export_path_pdf() -> str:
    from lynx_compare.export import default_export_path
    cr = _build_mock_comparison_result()
    return default_export_path(cr, ".pdf")


def get_default_export_path_txt() -> str:
    from lynx_compare.export import default_export_path
    cr = _build_mock_comparison_result()
    return default_export_path(cr, ".txt")


def export_to_nested_dir() -> str:
    """Export to a path whose parent directory does not yet exist."""
    from lynx_compare.export import export_comparison
    cr = _build_mock_comparison_result()
    nested = os.path.join(tempfile.mkdtemp(), "sub", "deep", "report.html")
    return export_comparison(cr, nested, "html")


def export_text_line_widths() -> list[int]:
    """Return lengths of all non-warning lines in the text export."""
    from lynx_compare.export import export_text
    cr = _build_mock_comparison_result()
    text = export_text(cr)
    return [
        len(line) for line in text.split("\n")
        if line and not line.startswith("  [")
    ]


def get_version() -> str:
    from lynx_compare import __version__
    return __version__


def get_about_app_name() -> str:
    from lynx_compare.about import APP_NAME
    return APP_NAME


def check_easter_egg_whitespace(text: str) -> bool:
    """Easter egg should handle whitespace around triggers."""
    from lynx_compare.about import check_easter_egg
    return check_easter_egg(text)


# ---------------------------------------------------------------------------
# ComparisonView API keywords
# ---------------------------------------------------------------------------

def get_comparison_view():
    """Build a ComparisonView from the mock result."""
    from lynx_compare.api import ComparisonView
    cr = _build_mock_comparison_result()
    return ComparisonView(cr)


def view_winner_ticker(view) -> str:
    return view.winner_ticker or "TIE"


def view_winner_name(view) -> str:
    return view.winner_name or "TIE"


def view_summary(view) -> str:
    return view.summary()


def view_section_names(view) -> list[str]:
    return view.section_names


def view_section_winner(view, section_name: str) -> str:
    return view.section_winner(section_name)


def view_section_winner_ticker(view, section_name: str) -> str:
    return view.section_winner_ticker(section_name) or "TIE"


def view_metric_winner(view, key: str) -> str:
    return view.metric_winner(key)


def view_metric_winner_ticker(view, key: str) -> str:
    return view.metric_winner_ticker(key) or "N/A"


def view_has_warnings(view) -> bool:
    return view.has_warnings


def view_to_dict(view) -> dict:
    return view.to_dict()


def view_scoreboard(view) -> dict:
    return view.scoreboard()


def view_metrics_won_by(view, ticker: str) -> int:
    return len(view.metrics_won_by(ticker))


def view_sections_won_by(view, ticker: str) -> int:
    return len(view.sections_won_by(ticker))


def view_repr(view) -> str:
    return repr(view)


# ---------------------------------------------------------------------------
# Warning keywords (detailed)
# ---------------------------------------------------------------------------

def build_mock_with_sector_mismatch():
    """Build a mock where sectors differ."""
    cr = _build_mock_comparison_result()
    cr.sector_a = "Technology"
    cr.sector_b = "Healthcare"
    cr.warnings = [
        from_lynx_compare_engine_Warning("sector", "Sector mismatch: AAPL (Technology) vs MSFT (Healthcare)"),
    ]
    return cr


def build_mock_with_tier_mismatch():
    """Build a mock where tiers differ."""
    from lynx_compare.engine import Warning
    cr = _build_mock_comparison_result()
    cr.tier_a = "Mega Cap"
    cr.tier_b = "Micro Cap"
    cr.warnings = [
        Warning(level="tier", message="Tier mismatch: AAPL (Mega Cap) vs MSFT (Micro Cap)"),
    ]
    return cr


def build_mock_with_all_warnings():
    """Build a mock with sector + industry + tier warnings."""
    from lynx_compare.engine import Warning
    cr = _build_mock_comparison_result()
    cr.sector_a = "Technology"
    cr.sector_b = "Healthcare"
    cr.tier_a = "Mega Cap"
    cr.tier_b = "Micro Cap"
    cr.warnings = [
        Warning(level="sector", message="Sector mismatch"),
        Warning(level="industry", message="Industry mismatch"),
        Warning(level="tier", message="Tier mismatch"),
    ]
    return cr


def from_lynx_compare_engine_Warning(level, message):
    """Helper to create a Warning object."""
    from lynx_compare.engine import Warning
    return Warning(level=level, message=message)


def count_warnings(cr) -> int:
    return len(cr.warnings)


def warning_levels(cr) -> list[str]:
    return [w.level for w in cr.warnings]


# ---------------------------------------------------------------------------
# GUI / module import keywords
# ---------------------------------------------------------------------------

def gui_module_importable() -> bool:
    """Check that the GUI module can be imported."""
    try:
        from lynx_compare.gui import app as _  # noqa: F401
        return True
    except Exception:
        return False


def tui_module_importable() -> bool:
    """Check that the TUI module can be imported."""
    try:
        from lynx_compare.tui import app as _  # noqa: F401
        return True
    except Exception:
        return False


def api_module_importable() -> bool:
    """Check that the API module can be imported."""
    try:
        from lynx_compare import api as _  # noqa: F401
        return True
    except Exception:
        return False


def export_module_importable() -> bool:
    """Check that the export module can be imported."""
    try:
        from lynx_compare import export as _  # noqa: F401
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Export format keywords
# ---------------------------------------------------------------------------

def export_text_contains_warnings() -> bool:
    """Check that text export includes warning text."""
    from lynx_compare.export import export_text
    cr = build_mock_with_all_warnings()
    text = export_text(cr)
    return "SECTOR" in text and "INDUSTRY" in text and "TIER" in text


def export_html_contains_warnings() -> bool:
    """Check that HTML export includes warning sections."""
    from lynx_compare.export import export_html
    cr = build_mock_with_all_warnings()
    html = export_html(cr)
    return "Sector" in html and "Industry" in html and "Tier" in html


def api_easter_egg_endpoint_has_art() -> bool:
    """Check that the easter egg endpoint returns ASCII art."""
    text = api_get_easter_egg()
    return "LYNX" in text and "o.o" in text

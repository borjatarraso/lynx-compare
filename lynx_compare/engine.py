"""Comparison engine — determines winners per metric, section, and overall."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from lynx.models import AnalysisReport


# ---------------------------------------------------------------------------
# Result data structures
# ---------------------------------------------------------------------------

@dataclass
class MetricResult:
    """Comparison result for a single metric."""
    key: str
    label: str
    value_a: object          # raw value (float, str, or None)
    value_b: object
    winner: str              # "a", "b", "tie", or "na"
    fmt_a: str = ""          # formatted display string (no Rich markup)
    fmt_b: str = ""


@dataclass
class SectionResult:
    """Comparison result for one section of metrics."""
    name: str
    metrics: list[MetricResult] = field(default_factory=list)
    wins_a: int = 0
    wins_b: int = 0
    ties: int = 0
    winner: str = "tie"      # "a", "b", or "tie"


@dataclass
class Warning:
    """A comparability warning."""
    level: str    # "sector", "industry", or "tier"
    message: str


@dataclass
class ComparisonResult:
    """Full comparison between two companies."""
    ticker_a: str
    ticker_b: str
    name_a: str
    name_b: str
    tier_a: str
    tier_b: str
    sector_a: str
    sector_b: str
    industry_a: str
    industry_b: str
    market_cap_a: Optional[float]
    market_cap_b: Optional[float]
    sections: list[SectionResult] = field(default_factory=list)
    warnings: list[Warning] = field(default_factory=list)
    total_wins_a: int = 0
    total_wins_b: int = 0
    total_ties: int = 0
    sections_won_a: int = 0
    sections_won_b: int = 0
    sections_tied: int = 0
    overall_winner: str = "tie"  # "a", "b", or "tie"


# ---------------------------------------------------------------------------
# Metric comparison rules
# ---------------------------------------------------------------------------

# Direction: how to determine the "better" value.
#   "higher"          — larger number wins
#   "lower"           — smaller number wins
#   "lower_positive"  — smaller wins, but negative values are penalised
#   "abs_lower"       — closer to zero wins (e.g. net debt)
#   "ordinal"         — compared via ORDINAL_RANKS

METRIC_DIRECTION: dict[str, str] = {
    # -- Valuation (cheaper is usually better) --
    "pe_trailing":           "lower_positive",
    "pe_forward":            "lower_positive",
    "pb_ratio":              "lower_positive",
    "ps_ratio":              "lower",
    "p_fcf":                 "lower_positive",
    "ev_ebitda":             "lower_positive",
    "ev_revenue":            "lower",
    "peg_ratio":             "lower_positive",
    "dividend_yield":        "higher",
    "earnings_yield":        "higher",
    "price_to_tangible_book":"lower_positive",
    "price_to_ncav":         "lower_positive",

    # -- Profitability (higher is better) --
    "roe":              "higher",
    "roa":              "higher",
    "roic":             "higher",
    "gross_margin":     "higher",
    "operating_margin": "higher",
    "net_margin":       "higher",
    "fcf_margin":       "higher",
    "ebitda_margin":    "higher",

    # -- Solvency --
    "debt_to_equity":    "lower",
    "debt_to_ebitda":    "lower",
    "current_ratio":     "higher",
    "quick_ratio":       "higher",
    "interest_coverage": "higher",
    "altman_z_score":    "higher",
    "net_debt":          "lower",
    "total_debt":        "lower",
    "total_cash":        "higher",
    "cash_burn_rate":    "higher",       # less-negative = better
    "cash_runway_years": "higher",
    "working_capital":   "higher",
    "cash_per_share":    "higher",
    "tangible_book_value":"higher",
    "ncav":              "higher",
    "ncav_per_share":    "higher",

    # -- Growth (higher is better, except dilution) --
    "revenue_growth_yoy":     "higher",
    "revenue_cagr_3y":        "higher",
    "revenue_cagr_5y":        "higher",
    "earnings_growth_yoy":    "higher",
    "earnings_cagr_3y":       "higher",
    "earnings_cagr_5y":       "higher",
    "fcf_growth_yoy":         "higher",
    "book_value_growth_yoy":  "higher",
    "dividend_growth_5y":     "higher",
    "shares_growth_yoy":      "lower",   # less dilution is better

    # -- Efficiency --
    "asset_turnover":          "higher",
    "inventory_turnover":      "higher",
    "receivables_turnover":    "higher",
    "days_sales_outstanding":  "lower",
    "days_inventory":          "lower",
    "cash_conversion_cycle":   "lower",

    # -- Moat --
    "moat_score":            "higher",
    "roic_consistency":      "ordinal",
    "margin_stability":      "ordinal",
    "revenue_predictability": "ordinal",
    "competitive_position":  "ordinal",
    "switching_costs":       "ordinal",
    "network_effects":       "ordinal",
    "cost_advantages":       "ordinal",
    "intangible_assets":     "ordinal",
    "efficient_scale":       "ordinal",
    "niche_position":        "ordinal",
    "insider_alignment":     "ordinal",
    "asset_backing":         "ordinal",

    # -- Intrinsic Value --
    "margin_of_safety_dcf":    "higher",
    "margin_of_safety_graham": "higher",
    "margin_of_safety_ncav":   "higher",
    "margin_of_safety_asset":  "higher",
}

# Ordinal rankings for qualitative moat fields (index = rank, higher = better).
ORDINAL_RANKS: dict[str, list[str]] = {
    "roic_consistency":       ["None", "Weak", "Moderate", "Strong"],
    "margin_stability":       ["Volatile", "Moderate", "Stable", "Very Stable"],
    "revenue_predictability": ["Declining", "Variable", "Positive", "Consistent", "Strong"],
    "competitive_position":   ["No Moat", "Weak", "Narrow", "Wide"],
}

# Generic fallback ranking for any ordinal field not in ORDINAL_RANKS.
_GENERIC_RANK = ["None", "No", "Weak", "Low", "Unlikely", "Possible",
                 "Moderate", "Medium", "Likely", "High", "Strong",
                 "Very High", "Very Strong", "Wide"]


def _ordinal_value(key: str, val: Optional[str]) -> Optional[int]:
    """Convert a qualitative string to an ordinal rank (higher = better).

    Uses substring matching so that descriptive values like
    "Very Stable (High)" match the rank "Very Stable".
    """
    if val is None:
        return None
    ranks = ORDINAL_RANKS.get(key, _GENERIC_RANK)
    normalized = val.strip().lower()
    # Try exact match first, then substring (longest match wins).
    best_rank = None
    best_len = 0
    for i, r in enumerate(ranks):
        rl = r.lower()
        if rl == normalized:
            return i
        if rl in normalized and len(rl) > best_len:
            best_rank = i
            best_len = len(rl)
    return best_rank


# ---------------------------------------------------------------------------
# Metric labels (human-readable names)
# ---------------------------------------------------------------------------

METRIC_LABELS: dict[str, str] = {
    # Valuation
    "pe_trailing":           "P/E (Trailing)",
    "pe_forward":            "P/E (Forward)",
    "pb_ratio":              "P/B Ratio",
    "ps_ratio":              "P/S Ratio",
    "p_fcf":                 "P/FCF",
    "ev_ebitda":             "EV/EBITDA",
    "ev_revenue":            "EV/Revenue",
    "peg_ratio":             "PEG Ratio",
    "dividend_yield":        "Dividend Yield",
    "earnings_yield":        "Earnings Yield",
    "price_to_tangible_book":"P/Tangible Book",
    "price_to_ncav":         "Price/NCAV",
    # Profitability
    "roe":              "Return on Equity",
    "roa":              "Return on Assets",
    "roic":             "Return on Invested Capital",
    "gross_margin":     "Gross Margin",
    "operating_margin": "Operating Margin",
    "net_margin":       "Net Margin",
    "fcf_margin":       "FCF Margin",
    "ebitda_margin":    "EBITDA Margin",
    # Solvency
    "debt_to_equity":    "Debt/Equity",
    "debt_to_ebitda":    "Debt/EBITDA",
    "current_ratio":     "Current Ratio",
    "quick_ratio":       "Quick Ratio",
    "interest_coverage": "Interest Coverage",
    "altman_z_score":    "Altman Z-Score",
    "net_debt":          "Net Debt",
    "total_debt":        "Total Debt",
    "total_cash":        "Total Cash",
    "cash_burn_rate":    "Cash Burn Rate",
    "cash_runway_years": "Cash Runway (Years)",
    "working_capital":   "Working Capital",
    "cash_per_share":    "Cash per Share",
    "tangible_book_value":"Tangible Book Value",
    "ncav":              "Net Current Asset Value",
    "ncav_per_share":    "NCAV per Share",
    # Growth
    "revenue_growth_yoy":     "Revenue Growth (YoY)",
    "revenue_cagr_3y":        "Revenue CAGR (3Y)",
    "revenue_cagr_5y":        "Revenue CAGR (5Y)",
    "earnings_growth_yoy":    "Earnings Growth (YoY)",
    "earnings_cagr_3y":       "Earnings CAGR (3Y)",
    "earnings_cagr_5y":       "Earnings CAGR (5Y)",
    "fcf_growth_yoy":         "FCF Growth (YoY)",
    "book_value_growth_yoy":  "Book Value Growth (YoY)",
    "dividend_growth_5y":     "Dividend Growth (5Y)",
    "shares_growth_yoy":      "Share Dilution (YoY)",
    # Efficiency
    "asset_turnover":          "Asset Turnover",
    "inventory_turnover":      "Inventory Turnover",
    "receivables_turnover":    "Receivables Turnover",
    "days_sales_outstanding":  "Days Sales Outstanding",
    "days_inventory":          "Days Inventory",
    "cash_conversion_cycle":   "Cash Conversion Cycle",
    # Moat
    "moat_score":            "Moat Score",
    "roic_consistency":      "ROIC Consistency",
    "margin_stability":      "Margin Stability",
    "revenue_predictability": "Revenue Predictability",
    "competitive_position":  "Competitive Position",
    "switching_costs":       "Switching Costs",
    "network_effects":       "Network Effects",
    "cost_advantages":       "Cost Advantages",
    "intangible_assets":     "Intangible Assets",
    "efficient_scale":       "Efficient Scale",
    "niche_position":        "Niche Position",
    "insider_alignment":     "Insider Alignment",
    "asset_backing":         "Asset Backing",
    # Intrinsic Value
    "dcf_value":               "DCF Value",
    "graham_number":           "Graham Number",
    "ncav_value":              "NCAV Value",
    "lynch_fair_value":        "Lynch Fair Value",
    "asset_based_value":       "Asset-Based Value",
    "current_price":           "Current Price",
    "margin_of_safety_dcf":    "Margin of Safety (DCF)",
    "margin_of_safety_graham": "Margin of Safety (Graham)",
    "margin_of_safety_ncav":   "Margin of Safety (NCAV)",
    "margin_of_safety_asset":  "Margin of Safety (Asset)",
    "primary_method":          "Primary Valuation Method",
    "secondary_method":        "Secondary Valuation Method",
}


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

# Sets of metric keys by format type.
_PCT_METRICS = {
    "dividend_yield", "earnings_yield",
    "roe", "roa", "roic",
    "gross_margin", "operating_margin", "net_margin", "fcf_margin", "ebitda_margin",
    "revenue_growth_yoy", "revenue_cagr_3y", "revenue_cagr_5y",
    "earnings_growth_yoy", "earnings_cagr_3y", "earnings_cagr_5y",
    "fcf_growth_yoy", "book_value_growth_yoy", "dividend_growth_5y",
    "shares_growth_yoy",
    "margin_of_safety_dcf", "margin_of_safety_graham",
    "margin_of_safety_ncav", "margin_of_safety_asset",
}

_MONEY_METRICS = {
    "enterprise_value", "market_cap",
    "net_debt", "total_debt", "total_cash",
    "cash_burn_rate", "working_capital", "tangible_book_value", "ncav",
    "dcf_value", "graham_number", "ncav_value", "lynch_fair_value",
    "asset_based_value", "current_price",
}

_MONEY_SMALL_METRICS = {
    "cash_per_share", "ncav_per_share", "book_value_per_share",
}

_SCORE_METRICS = {"moat_score"}

_STR_METRICS = {
    "roic_consistency", "margin_stability", "revenue_predictability",
    "competitive_position", "switching_costs", "network_effects",
    "cost_advantages", "intangible_assets", "efficient_scale",
    "niche_position", "insider_alignment", "asset_backing",
    "primary_method", "secondary_method",
}


def fmt_value(key: str, val: object) -> str:
    """Format a metric value as a plain display string."""
    if val is None:
        return "N/A"

    if key in _STR_METRICS:
        return str(val)

    if key in _SCORE_METRICS:
        return f"{float(val):.1f}/100"

    if key in _PCT_METRICS:
        return f"{float(val) * 100:.2f}%"

    if key in _MONEY_METRICS:
        v = float(val)
        neg = v < 0
        av = abs(v)
        if av >= 1_000_000_000_000:
            s = f"${av / 1_000_000_000_000:,.2f}T"
        elif av >= 1_000_000_000:
            s = f"${av / 1_000_000_000:,.2f}B"
        elif av >= 1_000_000:
            s = f"${av / 1_000_000:,.2f}M"
        else:
            s = f"${av:,.0f}"
        return f"-{s}" if neg else s

    if key in _MONEY_SMALL_METRICS:
        return f"${float(val):,.2f}"

    # Default numeric
    try:
        return f"{float(val):,.2f}"
    except (TypeError, ValueError):
        return str(val)


# ---------------------------------------------------------------------------
# Comparison logic
# ---------------------------------------------------------------------------

def _compare_numeric(
    a: Optional[float],
    b: Optional[float],
    direction: str,
) -> str:
    """Return 'a', 'b', 'tie', or 'na'."""
    if a is None and b is None:
        return "na"
    if a is None:
        return "b"
    if b is None:
        return "a"

    if direction == "lower_positive":
        # Negative values are penalised: positive beats negative.
        a_neg = a <= 0
        b_neg = b <= 0
        if a_neg and not b_neg:
            return "b"
        if b_neg and not a_neg:
            return "a"
        if a_neg and b_neg:
            return "na"   # both negative — not meaningful
        # Both positive: lower wins.
        if a < b:
            return "a"
        if b < a:
            return "b"
        return "tie"

    if direction in ("lower", "abs_lower"):
        if direction == "abs_lower":
            a, b = abs(a), abs(b)
        if a < b:
            return "a"
        if b < a:
            return "b"
        return "tie"

    # default: higher
    if a > b:
        return "a"
    if b > a:
        return "b"
    return "tie"


def _compare_metric(key: str, val_a: object, val_b: object) -> str:
    """Determine winner for a single metric."""
    direction = METRIC_DIRECTION.get(key, "higher")

    if direction == "ordinal":
        rank_a = _ordinal_value(key, val_a if isinstance(val_a, str) else None)
        rank_b = _ordinal_value(key, val_b if isinstance(val_b, str) else None)
        if rank_a is None and rank_b is None:
            return "na"
        if rank_a is None:
            return "b"
        if rank_b is None:
            return "a"
        if rank_a > rank_b:
            return "a"
        if rank_b > rank_a:
            return "b"
        return "tie"

    # Numeric comparison
    fa = float(val_a) if val_a is not None else None
    fb = float(val_b) if val_b is not None else None
    return _compare_numeric(fa, fb, direction)


# ---------------------------------------------------------------------------
# Section definitions
# ---------------------------------------------------------------------------

# Each section: (section_name, attribute on AnalysisReport, list of metric keys)

SECTIONS: list[tuple[str, str, list[str]]] = [
    ("Valuation", "valuation", [
        "pe_trailing", "pe_forward", "pb_ratio", "ps_ratio", "p_fcf",
        "ev_ebitda", "ev_revenue", "peg_ratio",
        "dividend_yield", "earnings_yield",
        "price_to_tangible_book", "price_to_ncav",
    ]),
    ("Profitability", "profitability", [
        "roe", "roa", "roic",
        "gross_margin", "operating_margin", "net_margin",
        "fcf_margin", "ebitda_margin",
    ]),
    ("Solvency", "solvency", [
        "debt_to_equity", "debt_to_ebitda",
        "current_ratio", "quick_ratio",
        "interest_coverage", "altman_z_score",
        "net_debt", "total_debt", "total_cash",
        "cash_burn_rate", "cash_runway_years",
        "working_capital", "cash_per_share",
        "tangible_book_value", "ncav", "ncav_per_share",
    ]),
    ("Growth", "growth", [
        "revenue_growth_yoy", "revenue_cagr_3y", "revenue_cagr_5y",
        "earnings_growth_yoy", "earnings_cagr_3y", "earnings_cagr_5y",
        "fcf_growth_yoy", "book_value_growth_yoy",
        "dividend_growth_5y", "shares_growth_yoy",
    ]),
    ("Efficiency", "efficiency", [
        "asset_turnover", "inventory_turnover", "receivables_turnover",
        "days_sales_outstanding", "days_inventory", "cash_conversion_cycle",
    ]),
    ("Moat", "moat", [
        "moat_score",
        "roic_consistency", "margin_stability",
        "revenue_predictability", "competitive_position",
        "switching_costs", "network_effects",
        "cost_advantages", "intangible_assets", "efficient_scale",
        "niche_position", "insider_alignment", "asset_backing",
    ]),
    ("Intrinsic Value", "intrinsic_value", [
        "dcf_value", "graham_number", "ncav_value",
        "lynch_fair_value", "asset_based_value", "current_price",
        "margin_of_safety_dcf", "margin_of_safety_graham",
        "margin_of_safety_ncav", "margin_of_safety_asset",
        "primary_method", "secondary_method",
    ]),
]

# Metrics that are informational only (no winner determination).
_INFO_ONLY = {
    "enterprise_value", "market_cap",
    "dcf_value", "graham_number", "ncav_value",
    "lynch_fair_value", "asset_based_value", "current_price",
    "primary_method", "secondary_method",
    # Descriptive moat fields — long text, not ordinal-comparable.
    "switching_costs", "network_effects",
    "cost_advantages", "intangible_assets", "efficient_scale",
    "niche_position", "insider_alignment", "asset_backing",
}


# ---------------------------------------------------------------------------
# Main comparison function
# ---------------------------------------------------------------------------

def compare(report_a: AnalysisReport, report_b: AnalysisReport) -> ComparisonResult:
    """Compare two analysis reports and return the full comparison result."""
    pa, pb = report_a.profile, report_b.profile

    result = ComparisonResult(
        ticker_a=pa.ticker,
        ticker_b=pb.ticker,
        name_a=pa.name,
        name_b=pb.name,
        tier_a=pa.tier.value,
        tier_b=pb.tier.value,
        sector_a=pa.sector or "N/A",
        sector_b=pb.sector or "N/A",
        industry_a=pa.industry or "N/A",
        industry_b=pb.industry or "N/A",
        market_cap_a=pa.market_cap,
        market_cap_b=pb.market_cap,
    )

    for section_name, attr_name, metric_keys in SECTIONS:
        obj_a = getattr(report_a, attr_name)
        obj_b = getattr(report_b, attr_name)

        section = SectionResult(name=section_name)

        for key in metric_keys:
            val_a = getattr(obj_a, key, None)
            val_b = getattr(obj_b, key, None)

            label = METRIC_LABELS.get(key, key.replace("_", " ").title())

            if key in _INFO_ONLY:
                winner = "na"
            else:
                winner = _compare_metric(key, val_a, val_b)

            mr = MetricResult(
                key=key,
                label=label,
                value_a=val_a,
                value_b=val_b,
                winner=winner,
                fmt_a=fmt_value(key, val_a),
                fmt_b=fmt_value(key, val_b),
            )
            section.metrics.append(mr)

            if winner == "a":
                section.wins_a += 1
            elif winner == "b":
                section.wins_b += 1
            elif winner == "tie":
                section.ties += 1

        # Section winner
        if section.wins_a > section.wins_b:
            section.winner = "a"
        elif section.wins_b > section.wins_a:
            section.winner = "b"
        else:
            section.winner = "tie"

        result.sections.append(section)

        # Accumulate totals
        result.total_wins_a += section.wins_a
        result.total_wins_b += section.wins_b
        result.total_ties += section.ties

        if section.winner == "a":
            result.sections_won_a += 1
        elif section.winner == "b":
            result.sections_won_b += 1
        else:
            result.sections_tied += 1

    # Overall winner: decided by sections won, tie-broken by total metric wins.
    if result.sections_won_a > result.sections_won_b:
        result.overall_winner = "a"
    elif result.sections_won_b > result.sections_won_a:
        result.overall_winner = "b"
    elif result.total_wins_a > result.total_wins_b:
        result.overall_winner = "a"
    elif result.total_wins_b > result.total_wins_a:
        result.overall_winner = "b"
    else:
        result.overall_winner = "tie"

    # --- Comparability warnings (non-exclusive — all three can fire) ---
    # Sector mismatch (most severe — blinking red)
    if (
        result.sector_a != "N/A"
        and result.sector_b != "N/A"
        and result.sector_a.lower() != result.sector_b.lower()
    ):
        result.warnings.append(Warning(
            level="sector",
            message=(
                f"Sector mismatch: {pa.ticker} ({result.sector_a}) "
                f"vs {pb.ticker} ({result.sector_b})"
            ),
        ))

    # Industry mismatch (medium — blinking orange)
    if (
        result.industry_a != "N/A"
        and result.industry_b != "N/A"
        and result.industry_a.lower() != result.industry_b.lower()
    ):
        result.warnings.append(Warning(
            level="industry",
            message=(
                f"Industry mismatch: {pa.ticker} ({result.industry_a}) "
                f"vs {pb.ticker} ({result.industry_b})"
            ),
        ))

    # Tier mismatch (lower severity — blinking yellow)
    if result.tier_a != result.tier_b:
        result.warnings.append(Warning(
            level="tier",
            message=(
                f"Tier mismatch: {pa.ticker} ({result.tier_a}) "
                f"vs {pb.ticker} ({result.tier_b})"
            ),
        ))

    return result

"""N-way comparison for Lynx Compare (v5.1).

The original :func:`lynx_compare.engine.compare` is strictly binary —
`report_a` vs `report_b`. This module builds on the same
``METRIC_DIRECTION`` + ``SECTIONS`` knowledge to compare **N** companies
at once and return a multi-column result suitable for a Rich table /
JSON / PDF.

Algorithm (per metric):

1. Collect every participating report's value for the metric.
2. Drop ``None`` and purely-informational fields.
3. Apply the direction (``higher``, ``lower``, ``lower_positive``,
   ``abs_lower``) to rank the survivors.
4. The top-ranked ticker is the **winner**; ties mark every tied
   ticker as co-winners.

The *overall* winner is the ticker with the most per-metric wins;
ties produce ``overall_winner=None``.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from lynx.models import AnalysisReport

from lynx_compare.engine import (
    METRIC_DIRECTION,
    METRIC_LABELS,
    SECTIONS,
    _INFO_ONLY,
    _ordinal_value,
    fmt_value,
)


__all__ = [
    "MultiMetricResult",
    "MultiSectionResult",
    "MultiComparisonResult",
    "compare_many",
    "compare_many_reports",
]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class MultiMetricResult:
    key: str
    label: str
    section: str
    direction: str
    values: Dict[str, Any]           # ticker → raw value
    formatted: Dict[str, str]        # ticker → formatted string
    winners: List[str]               # co-winners (ties possible)


@dataclass
class MultiSectionResult:
    section: str
    metrics: List[MultiMetricResult] = field(default_factory=list)
    winners: List[str] = field(default_factory=list)  # section champions


@dataclass
class MultiComparisonResult:
    tickers: List[str]
    sections: List[MultiSectionResult]
    overall_winner: Optional[str]
    wins_by_ticker: Dict[str, int]

    def as_dict(self) -> Dict:
        return {
            "tickers": self.tickers,
            "overall_winner": self.overall_winner,
            "wins_by_ticker": self.wins_by_ticker,
            "sections": [
                {
                    "section": s.section,
                    "winners": s.winners,
                    "metrics": [
                        {
                            "key": m.key,
                            "label": m.label,
                            "section": m.section,
                            "direction": m.direction,
                            "values": m.values,
                            "formatted": m.formatted,
                            "winners": m.winners,
                        }
                        for m in s.metrics
                    ],
                }
                for s in self.sections
            ],
        }

    def summary(self) -> str:
        if not self.tickers:
            return "(no tickers)"
        header = ", ".join(self.tickers)
        if self.overall_winner is None:
            return f"{header} — no clear winner (tie)."
        return f"{header} — overall winner: {self.overall_winner}."


# ---------------------------------------------------------------------------
# Ranking helpers
# ---------------------------------------------------------------------------

def _score_for(direction: str, value: Any, metric_key: Optional[str] = None) -> Optional[float]:
    """Return a sortable float with "higher = better" semantics."""
    if value is None:
        return None
    if isinstance(value, str):
        if value.upper() in ("N/A", "NA", ""):
            return None
        # Try ordinal mapping (e.g. tier, stage).
        ord_val = _ordinal_value(metric_key, value) if metric_key else None
        if ord_val is not None:
            return float(ord_val)
        # Can't interpret as numeric.
        return None

    try:
        v = float(value)
    except (TypeError, ValueError):
        return None

    if direction == "lower_positive":
        if v <= 0:
            return -1e18          # pathological
        return -v                  # lower value → higher score
    if direction == "abs_lower":
        return -abs(v)
    if direction == "lower":
        return -v
    return v                       # default: higher is better


def _pick_winners(values_by_ticker: Dict[str, Any], direction: str,
                  metric_key: Optional[str] = None) -> List[str]:
    """Return the ticker(s) with the best score for this metric."""
    best_score: Optional[float] = None
    best: List[str] = []
    for ticker, val in values_by_ticker.items():
        score = _score_for(direction, val, metric_key=metric_key)
        if score is None:
            continue
        if best_score is None or score > best_score + 1e-12:
            best_score = score
            best = [ticker]
        elif abs(score - best_score) <= 1e-12:
            best.append(ticker)
    return best


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compare_many_reports(reports: Sequence[AnalysisReport]) -> MultiComparisonResult:
    """Compare two or more :class:`AnalysisReport` objects."""
    if not reports:
        return MultiComparisonResult(tickers=[], sections=[],
                                     overall_winner=None, wins_by_ticker={})

    tickers: List[str] = []
    ticker_to_report: Dict[str, AnalysisReport] = {}
    for r in reports:
        if r is None or r.profile is None or not r.profile.ticker:
            continue
        tickers.append(r.profile.ticker)
        ticker_to_report[r.profile.ticker] = r
    if len(tickers) < 2:
        return MultiComparisonResult(tickers=tickers, sections=[],
                                     overall_winner=None, wins_by_ticker={})

    sections_out: List[MultiSectionResult] = []
    wins_counter: Counter = Counter()

    for section_name, attr_name, metric_keys in SECTIONS:
        sec_res = MultiSectionResult(section=section_name)
        section_wins: Counter = Counter()

        for metric_key in metric_keys:
            direction = METRIC_DIRECTION.get(metric_key, "higher")
            label = METRIC_LABELS.get(metric_key, metric_key.replace("_", " ").title())
            values = {
                t: getattr(getattr(ticker_to_report[t], attr_name, None), metric_key, None)
                for t in tickers
            }
            formatted = {t: fmt_value(metric_key, v) for t, v in values.items()}
            if metric_key in _INFO_ONLY:
                winners: List[str] = []
            else:
                winners = _pick_winners(values, direction, metric_key=metric_key)
            sec_res.metrics.append(MultiMetricResult(
                key=metric_key, label=label, section=section_name,
                direction=direction, values=values, formatted=formatted,
                winners=winners,
            ))
            for w in winners:
                section_wins[w] += 1
                wins_counter[w] += 1

        if section_wins:
            top = max(section_wins.values())
            sec_res.winners = [t for t, v in section_wins.items() if v == top]
        sections_out.append(sec_res)

    wins_by_ticker = {t: wins_counter.get(t, 0) for t in tickers}
    if wins_counter:
        top = max(wins_counter.values())
        champions = [t for t in tickers if wins_counter[t] == top]
        overall = champions[0] if len(champions) == 1 else None
    else:
        overall = None

    return MultiComparisonResult(
        tickers=tickers,
        sections=sections_out,
        overall_winner=overall,
        wins_by_ticker=wins_by_ticker,
    )


def compare_many(
    *identifiers: str,
    refresh: bool = False,
    download_reports: bool = False,
    download_news: bool = False,
    verbose: bool = False,
) -> MultiComparisonResult:
    """Run analysis for every identifier and compare them.

    Requires at least two identifiers; silently returns an empty result
    when fewer are supplied. Identifiers that fail analysis are skipped
    (callers can check ``result.tickers`` vs their input to detect drops).
    """
    from lynx.core.analyzer import run_full_analysis

    reports: List[AnalysisReport] = []
    for ident in identifiers:
        try:
            r = run_full_analysis(
                identifier=ident,
                download_reports=download_reports,
                download_news=download_news,
                verbose=verbose,
                refresh=refresh,
            )
            reports.append(r)
        except Exception:
            continue
    return compare_many_reports(reports)

"""Public Python API for Lynx Compare.

Provides programmatic access to the comparison engine without any
terminal rendering.  All functions return plain dataclasses that
can be serialised to JSON / consumed by other tools.

Quick start
-----------
>>> from lynx.core.storage import set_mode
>>> set_mode("production")
>>>
>>> from lynx_compare.api import compare_companies, compare_reports
>>> result = compare_companies("AAPL", "MSFT")
>>> result.overall_winner          # "a", "b", or "tie"
>>> result.winner_ticker           # "AAPL" or "MSFT"
>>> result.summary()               # human-readable one-liner
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Optional

from lynx.models import AnalysisReport

from lynx_compare.engine import (
    ComparisonResult,
    MetricResult,
    SectionResult,
    Warning,
    compare,
    fmt_value,
)


# ---------------------------------------------------------------------------
# High-level convenience API
# ---------------------------------------------------------------------------

def compare_companies(
    identifier_a: str,
    identifier_b: str,
    *,
    refresh: bool = False,
    download_reports: bool = False,
    download_news: bool = False,
    verbose: bool = False,
) -> ComparisonView:
    """Compare two companies end-to-end and return a rich result view.

    This is the main entry point for library users.  It resolves
    identifiers, runs fundamental analysis for both companies
    (using lynx-fa), and returns a ``ComparisonView`` wrapping the
    full comparison.

    Parameters
    ----------
    identifier_a : str
        Ticker, ISIN, or company name for the first company.
    identifier_b : str
        Ticker, ISIN, or company name for the second company.
    refresh : bool
        Force fresh data download (ignore lynx-fa cache).
    download_reports : bool
        Fetch SEC filings during analysis.
    download_news : bool
        Fetch news articles during analysis.
    verbose : bool
        Enable verbose output from lynx-fa.

    Returns
    -------
    ComparisonView
        A convenience wrapper around ``ComparisonResult`` with
        helper methods for querying winners, sections, and metrics.

    Raises
    ------
    ValueError
        If either identifier cannot be resolved.

    Example
    -------
    >>> from lynx.core.storage import set_mode
    >>> set_mode("production")
    >>> result = compare_companies("AAPL", "MSFT")
    >>> print(result.winner_ticker)
    'MSFT'
    >>> print(result.section_winner("Profitability"))
    'AAPL'
    """
    from lynx.core.analyzer import run_full_analysis

    report_a = run_full_analysis(
        identifier=identifier_a,
        download_reports=download_reports,
        download_news=download_news,
        verbose=verbose,
        refresh=refresh,
    )
    report_b = run_full_analysis(
        identifier=identifier_b,
        download_reports=download_reports,
        download_news=download_news,
        verbose=verbose,
        refresh=refresh,
    )

    return compare_reports(report_a, report_b)


def compare_reports(
    report_a: AnalysisReport,
    report_b: AnalysisReport,
) -> ComparisonView:
    """Compare two pre-built ``AnalysisReport`` objects.

    Use this when you already have the reports (e.g. loaded from
    cache or built with custom parameters) and want to avoid a
    second resolution / fetch cycle.

    Parameters
    ----------
    report_a : AnalysisReport
        First company's analysis report.
    report_b : AnalysisReport
        Second company's analysis report.

    Returns
    -------
    ComparisonView

    Example
    -------
    >>> from lynx.core.storage import set_mode
    >>> from lynx.core.analyzer import run_full_analysis
    >>> set_mode("production")
    >>> a = run_full_analysis("AAPL")
    >>> b = run_full_analysis("MSFT")
    >>> view = compare_reports(a, b)
    >>> view.overall_winner
    'b'
    """
    raw = compare(report_a, report_b)
    return ComparisonView(raw)


# ---------------------------------------------------------------------------
# ComparisonView — convenience wrapper
# ---------------------------------------------------------------------------

class ComparisonView:
    """Read-only view over a ``ComparisonResult`` with helper methods.

    Attributes
    ----------
    raw : ComparisonResult
        The underlying dataclass — access this for full detail.
    """

    def __init__(self, result: ComparisonResult) -> None:
        self.raw = result

    # -- Identity ----------------------------------------------------------

    @property
    def ticker_a(self) -> str:
        """Ticker symbol of the first company."""
        return self.raw.ticker_a

    @property
    def ticker_b(self) -> str:
        """Ticker symbol of the second company."""
        return self.raw.ticker_b

    @property
    def name_a(self) -> str:
        """Full name of the first company."""
        return self.raw.name_a

    @property
    def name_b(self) -> str:
        """Full name of the second company."""
        return self.raw.name_b

    # -- Overall winner ----------------------------------------------------

    @property
    def overall_winner(self) -> str:
        """Overall winner as ``"a"``, ``"b"``, or ``"tie"``."""
        return self.raw.overall_winner

    @property
    def winner_ticker(self) -> Optional[str]:
        """Ticker of the overall winner, or ``None`` on tie."""
        if self.raw.overall_winner == "a":
            return self.raw.ticker_a
        if self.raw.overall_winner == "b":
            return self.raw.ticker_b
        return None

    @property
    def winner_name(self) -> Optional[str]:
        """Company name of the overall winner, or ``None`` on tie."""
        if self.raw.overall_winner == "a":
            return self.raw.name_a
        if self.raw.overall_winner == "b":
            return self.raw.name_b
        return None

    # -- Tallies -----------------------------------------------------------

    @property
    def sections_won_a(self) -> int:
        return self.raw.sections_won_a

    @property
    def sections_won_b(self) -> int:
        return self.raw.sections_won_b

    @property
    def total_wins_a(self) -> int:
        return self.raw.total_wins_a

    @property
    def total_wins_b(self) -> int:
        return self.raw.total_wins_b

    @property
    def total_ties(self) -> int:
        return self.raw.total_ties

    # -- Warnings ----------------------------------------------------------

    @property
    def warnings(self) -> list[Warning]:
        """Comparability warnings (sector/industry/tier mismatches)."""
        return self.raw.warnings

    @property
    def has_warnings(self) -> bool:
        return len(self.raw.warnings) > 0

    # -- Section access ----------------------------------------------------

    @property
    def section_names(self) -> list[str]:
        """Ordered list of section names."""
        return [s.name for s in self.raw.sections]

    def section(self, name: str) -> SectionResult:
        """Get a section by name (case-insensitive).

        Raises ``KeyError`` if not found.

        Example
        -------
        >>> s = view.section("Valuation")
        >>> s.winner      # "a", "b", or "tie"
        >>> s.wins_a      # number of metrics won by company A
        """
        key = name.lower()
        for s in self.raw.sections:
            if s.name.lower() == key:
                return s
        raise KeyError(f"No section named '{name}'. Available: {self.section_names}")

    def section_winner(self, name: str) -> str:
        """Winner of a named section: ``"a"``, ``"b"``, or ``"tie"``.

        Example
        -------
        >>> view.section_winner("Profitability")
        'a'
        """
        return self.section(name).winner

    def section_winner_ticker(self, name: str) -> Optional[str]:
        """Ticker of the section winner, or ``None`` on tie."""
        w = self.section_winner(name)
        if w == "a":
            return self.raw.ticker_a
        if w == "b":
            return self.raw.ticker_b
        return None

    # -- Metric access -----------------------------------------------------

    def metric(self, key: str) -> MetricResult:
        """Look up a single metric result by key across all sections.

        Raises ``KeyError`` if the metric key is not found.

        Example
        -------
        >>> m = view.metric("pe_trailing")
        >>> m.value_a     # 33.01
        >>> m.value_b     # 36.42
        >>> m.winner      # "a"
        >>> m.fmt_a       # "33.01"
        """
        for s in self.raw.sections:
            for m in s.metrics:
                if m.key == key:
                    return m
        raise KeyError(f"No metric with key '{key}'")

    def metric_winner(self, key: str) -> str:
        """Winner for a specific metric: ``"a"``, ``"b"``, ``"tie"``, or ``"na"``.

        Example
        -------
        >>> view.metric_winner("roic")
        'a'
        """
        return self.metric(key).winner

    def metric_winner_ticker(self, key: str) -> Optional[str]:
        """Ticker of the metric winner, or ``None`` on tie/na."""
        w = self.metric_winner(key)
        if w == "a":
            return self.raw.ticker_a
        if w == "b":
            return self.raw.ticker_b
        return None

    def metrics_won_by(self, ticker: str) -> list[MetricResult]:
        """Return all metrics won by the given ticker.

        Example
        -------
        >>> for m in view.metrics_won_by("AAPL"):
        ...     print(m.label, m.fmt_a)
        """
        side = self._ticker_to_side(ticker)
        return [
            m
            for s in self.raw.sections
            for m in s.metrics
            if m.winner == side
        ]

    def sections_won_by(self, ticker: str) -> list[SectionResult]:
        """Return all sections won by the given ticker.

        Example
        -------
        >>> for s in view.sections_won_by("MSFT"):
        ...     print(s.name, s.wins_b)
        """
        side = self._ticker_to_side(ticker)
        return [s for s in self.raw.sections if s.winner == side]

    # -- Serialisation -----------------------------------------------------

    def summary(self) -> str:
        """One-line human-readable summary.

        Example
        -------
        >>> view.summary()
        'MSFT wins 6-1 sections (30-15 metrics) vs AAPL'
        """
        r = self.raw
        if r.overall_winner == "a":
            return (
                f"{r.ticker_a} wins {r.sections_won_a}-{r.sections_won_b} sections "
                f"({r.total_wins_a}-{r.total_wins_b} metrics) vs {r.ticker_b}"
            )
        if r.overall_winner == "b":
            return (
                f"{r.ticker_b} wins {r.sections_won_b}-{r.sections_won_a} sections "
                f"({r.total_wins_b}-{r.total_wins_a} metrics) vs {r.ticker_a}"
            )
        return (
            f"Tie: {r.ticker_a} {r.sections_won_a}-{r.sections_won_b} {r.ticker_b} "
            f"({r.total_wins_a}-{r.total_wins_b} metrics)"
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialise the full comparison to a plain dict (JSON-friendly).

        Example
        -------
        >>> import json
        >>> print(json.dumps(view.to_dict(), indent=2))
        """
        return asdict(self.raw)

    def scoreboard(self) -> dict[str, dict[str, Any]]:
        """Section-by-section scoreboard as a dict.

        Returns a dict keyed by section name, each containing:
        ``wins_a``, ``wins_b``, ``ties``, ``winner``,
        ``winner_ticker``.

        Example
        -------
        >>> for name, info in view.scoreboard().items():
        ...     print(f"{name}: {info['winner_ticker']} wins")
        """
        board: dict[str, dict[str, Any]] = {}
        for s in self.raw.sections:
            wt = None
            if s.winner == "a":
                wt = self.raw.ticker_a
            elif s.winner == "b":
                wt = self.raw.ticker_b
            board[s.name] = {
                "wins_a": s.wins_a,
                "wins_b": s.wins_b,
                "ties": s.ties,
                "winner": s.winner,
                "winner_ticker": wt,
            }
        return board

    # -- Internal ----------------------------------------------------------

    def _ticker_to_side(self, ticker: str) -> str:
        t = ticker.upper()
        if t == self.raw.ticker_a.upper():
            return "a"
        if t == self.raw.ticker_b.upper():
            return "b"
        raise ValueError(
            f"'{ticker}' is not one of the compared tickers "
            f"({self.raw.ticker_a}, {self.raw.ticker_b})"
        )

    def __repr__(self) -> str:
        return (
            f"ComparisonView({self.raw.ticker_a} vs {self.raw.ticker_b}, "
            f"winner={self.winner_ticker or 'TIE'})"
        )

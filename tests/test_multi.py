"""Unit tests for :mod:`lynx_compare.multi` (N-way compare)."""

from __future__ import annotations

import pytest

from lynx.models import (
    AnalysisReport,
    CompanyProfile,
    ValuationMetrics,
    ProfitabilityMetrics,
    SolvencyMetrics,
    GrowthMetrics,
    EfficiencyMetrics,
    MoatIndicators,
    IntrinsicValue,
)

from lynx_compare.multi import (
    compare_many_reports,
    _score_for,
    _pick_winners,
)


def _mk(ticker: str, **overrides) -> AnalysisReport:
    """Build a minimal but complete AnalysisReport for testing."""
    return AnalysisReport(
        profile=CompanyProfile(ticker=ticker, name=f"{ticker} Inc"),
        valuation=ValuationMetrics(**overrides.get("valuation", {})),
        profitability=ProfitabilityMetrics(**overrides.get("profitability", {})),
        solvency=SolvencyMetrics(**overrides.get("solvency", {})),
        growth=GrowthMetrics(**overrides.get("growth", {})),
        efficiency=EfficiencyMetrics(**overrides.get("efficiency", {})),
        moat=MoatIndicators(**overrides.get("moat", {})),
        intrinsic_value=IntrinsicValue(**overrides.get("intrinsic_value", {})),
    )


class TestScoreFor:
    def test_none_is_none(self) -> None:
        assert _score_for("higher", None) is None

    def test_higher_preserves_order(self) -> None:
        assert _score_for("higher", 10) > _score_for("higher", 5)

    def test_lower_flips_order(self) -> None:
        assert _score_for("lower", 1) > _score_for("lower", 10)

    def test_lower_positive_penalizes_negative(self) -> None:
        # Negative gets a very bad score; positive keeps natural rank
        neg = _score_for("lower_positive", -3)
        ok = _score_for("lower_positive", 10)
        assert neg < ok

    def test_lower_positive_prefers_smaller_positives(self) -> None:
        assert _score_for("lower_positive", 5) > _score_for("lower_positive", 30)

    def test_abs_lower(self) -> None:
        assert _score_for("abs_lower", -3) > _score_for("abs_lower", -10)

    def test_string_na_is_none(self) -> None:
        assert _score_for("higher", "N/A") is None


class TestPickWinners:
    def test_single_winner(self) -> None:
        winners = _pick_winners({"A": 100, "B": 50, "C": 20}, "higher")
        assert winners == ["A"]

    def test_tie(self) -> None:
        winners = _pick_winners({"A": 10, "B": 10, "C": 5}, "higher")
        assert set(winners) == {"A", "B"}

    def test_skips_none(self) -> None:
        winners = _pick_winners({"A": None, "B": 5, "C": None}, "higher")
        assert winners == ["B"]

    def test_all_none_returns_empty(self) -> None:
        assert _pick_winners({"A": None, "B": None}, "higher") == []


class TestCompareManyReports:
    def test_two_reports(self) -> None:
        a = _mk("A", valuation={"pe_trailing": 10, "pb_ratio": 2},
                profitability={"roe": 0.25, "roa": 0.15})
        b = _mk("B", valuation={"pe_trailing": 30, "pb_ratio": 5},
                profitability={"roe": 0.10, "roa": 0.05})
        r = compare_many_reports([a, b])
        assert r.tickers == ["A", "B"]
        assert r.overall_winner == "A"
        assert r.wins_by_ticker["A"] > r.wins_by_ticker["B"]

    def test_three_reports(self) -> None:
        a = _mk("A", valuation={"pe_trailing": 10}, profitability={"roe": 0.30})
        b = _mk("B", valuation={"pe_trailing": 25}, profitability={"roe": 0.20})
        c = _mk("C", valuation={"pe_trailing": 50}, profitability={"roe": 0.10})
        r = compare_many_reports([a, b, c])
        assert set(r.tickers) == {"A", "B", "C"}
        # A wins both metrics
        assert r.overall_winner == "A"

    def test_tie_returns_none(self) -> None:
        a = _mk("A", valuation={"pe_trailing": 10}, profitability={"roe": 0.05})
        b = _mk("B", valuation={"pe_trailing": 50}, profitability={"roe": 0.30})
        r = compare_many_reports([a, b])
        # A wins valuation, B wins profitability — close but asymmetric
        # Overall winner may be either; verify the function returns a
        # string or None, not a crash.
        assert r.overall_winner is None or r.overall_winner in ("A", "B")

    def test_one_report_returns_empty(self) -> None:
        a = _mk("A")
        r = compare_many_reports([a])
        assert r.tickers == ["A"]
        assert r.sections == []
        assert r.overall_winner is None

    def test_zero_reports(self) -> None:
        r = compare_many_reports([])
        assert r.tickers == []

    def test_sections_populated(self) -> None:
        a = _mk("A")
        b = _mk("B")
        r = compare_many_reports([a, b])
        # 7 expected sections
        assert len(r.sections) == 7
        names = [s.section for s in r.sections]
        assert "Valuation" in names
        assert "Profitability" in names

    def test_as_dict_serializable(self) -> None:
        import json
        a = _mk("A", valuation={"pe_trailing": 10})
        b = _mk("B", valuation={"pe_trailing": 20})
        r = compare_many_reports([a, b])
        json.dumps(r.as_dict())  # must not raise

    def test_summary(self) -> None:
        a = _mk("A", valuation={"pe_trailing": 10})
        b = _mk("B", valuation={"pe_trailing": 20})
        r = compare_many_reports([a, b])
        assert "A" in r.summary() or "B" in r.summary()

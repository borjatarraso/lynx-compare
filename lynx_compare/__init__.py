"""Lynx Compare — Side-by-side fundamental analysis comparison tool.

Public API
----------
>>> from lynx.core.storage import set_mode
>>> set_mode("production")
>>>
>>> from lynx_compare.api import compare_companies, compare_reports
>>> result = compare_companies("AAPL", "MSFT")
>>> result.winner_ticker
'MSFT'
"""

__version__ = "1.1"
__author__ = "Borja Tarraso <borja.tarraso@member.fsf.org>"
__year__ = "2026"


def __getattr__(name: str):
    """Lazy imports to avoid circular-import issues with cli.py."""
    _api_names = {
        "compare_companies", "compare_reports", "ComparisonView",
    }
    _engine_names = {
        "ComparisonResult", "MetricResult", "SectionResult",
        "Warning", "compare",
    }
    if name in _api_names:
        from lynx_compare import api
        return getattr(api, name)
    if name in _engine_names:
        from lynx_compare import engine
        return getattr(engine, name)
    raise AttributeError(f"module 'lynx_compare' has no attribute {name!r}")


__all__ = [
    "compare_companies",
    "compare_reports",
    "ComparisonView",
    "ComparisonResult",
    "MetricResult",
    "SectionResult",
    "Warning",
    "compare",
]

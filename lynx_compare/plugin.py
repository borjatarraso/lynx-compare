"""Entry-point registration for the Lince Investor Suite plugin system.

Exposed via ``pyproject.toml`` under the ``lynx_investor_suite.agents``
entry-point group. See :mod:`lynx_investor_core.plugins` for the
discovery contract.
"""

from __future__ import annotations

from lynx_investor_core.plugins import SectorAgent

from lynx_compare import __version__


def register() -> SectorAgent:
    """Return this agent's descriptor for the plugin registry."""
    return SectorAgent(
        name="lynx-compare",
        short_name="compare",
        sector="Comparison tool",
        tagline="Side-by-side comparison of two companies across every lens",
        prog_name="lynx-compare",
        version=__version__,
        package_module="lynx_compare",
        entry_point_module="lynx_compare.__main__",
        entry_point_function="main",
        icon="\u2696",  # scales
    )

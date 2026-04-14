"""Export comparison results to PDF, HTML, and plain-text files.

All exports use a clean white background with dark text regardless of
the application theme, ensuring readability when printed or shared.
"""

from __future__ import annotations

import html as _html
import os
from pathlib import Path
from typing import Optional

from lynx_compare import __version__, __year__
from lynx_compare.about import APP_NAME, DEVELOPER, LICENSE_NAME
from lynx_compare.engine import ComparisonResult, SectionResult, fmt_value


# ---------------------------------------------------------------------------
# Unicode symbols (used in HTML/PDF export where rendering is reliable)
# ---------------------------------------------------------------------------
CHECK = "\u2714"       # ✔
CROSS = "\u2718"       # ✘
TROPHY = "\u2605"      # ★
CROWN = "\u2654"       # ♔
ARROW_L = "<<<"
ARROW_R = ">>>"
TIE_S = "<=>"


def _winner_arrow(winner: str) -> str:
    if winner == "a":
        return ARROW_L
    if winner == "b":
        return ARROW_R
    if winner == "tie":
        return TIE_S
    return "---"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_mcap(val: float | None) -> str:
    if val is None:
        return "N/A"
    av = abs(val)
    if av >= 1e12:
        return f"${av / 1e12:,.2f}T"
    if av >= 1e9:
        return f"${av / 1e9:,.2f}B"
    if av >= 1e6:
        return f"${av / 1e6:,.2f}M"
    return f"${av:,.0f}"


# ===================================================================
# Plain-text export
# ===================================================================
#
# All columns are pure ASCII so alignment is consistent across every
# monospace font and text editor.  The total line width is 80 chars.
#
# Metric rows use a 5-column layout:
#   Value_A (20 right) | Arrow (5 center) | Metric (24 center)
#                       | Arrow (5 center) | Value_B (20 left)
#   20 + 1 + 5 + 1 + 24 + 1 + 5 + 1 + 20 = 78 (+ 2 edge pad = 80)

_W = 80          # page width
_VA = 19         # value-A column (right-aligned)
_AR = 5          # arrow column (centred)
_MT = 22         # metric column (centred)
_VB = 19         # value-B column (left-aligned)
# Gaps are single spaces; total = 19+1+5+1+22+1+5+1+19 = 74.  Pad to 80 with
# 3-char left margin on each side.
_PAD = "   "     # left/right margin to reach 80


def _row(va: str, al: str, metric: str, ar: str, vb: str) -> str:
    """Build one fixed-width metric row."""
    return (
        f"{_PAD}"
        f"{va:>{_VA}} "
        f"{al:^{_AR}} "
        f"{metric:^{_MT}} "
        f"{ar:^{_AR}} "
        f"{vb:<{_VB}}"
        f"{_PAD}"
    )


def _sep() -> str:
    """Build a separator row matching the metric columns."""
    return _row("-" * _VA, "-" * _AR, "-" * _MT, "-" * _AR, "-" * _VB)


def _profile_row(va: str, metric: str, vb: str) -> str:
    """Build one profile row (no arrow columns, fits in 80 chars)."""
    col_a = 23
    col_m = 22
    col_b = 23
    # Truncate long values to keep lines within 80 chars
    if len(va) > col_a:
        va = va[:col_a - 1] + "~"
    if len(vb) > col_b:
        vb = vb[:col_b - 1] + "~"
    return f"  {va:>{col_a}}   {metric:^{col_m}}   {vb:<{col_b}}"


def export_text(cr: ComparisonResult) -> str:
    """Render comparison as a well-formatted plain-text report.

    Uses pure-ASCII characters for all alignment-critical elements
    so the output looks correct in any monospace font.
    """
    lines: list[str] = []

    # ── Header ──────────────────────────────────────────────────────
    lines.append("=" * _W)
    lines.append(f"{APP_NAME} v{__version__}  --  Comparison Report".center(_W))
    matchup = f"{cr.name_a} ({cr.ticker_a})  vs  {cr.name_b} ({cr.ticker_b})"
    lines.append(matchup.center(_W))
    lines.append("=" * _W)
    lines.append("")

    # ── Warnings ────────────────────────────────────────────────────
    if cr.warnings:
        lines.append("WARNINGS:")
        for w in cr.warnings:
            lines.append(f"  [{w.level.upper()}] {w.message}")
        lines.append("")

    # ── Profile ─────────────────────────────────────────────────────
    lines.append("-" * _W)
    lines.append("COMPANY PROFILE".center(_W))
    lines.append("-" * _W)
    lines.append(_profile_row(cr.ticker_a, "Metric", cr.ticker_b))
    lines.append(_profile_row("-" * 24, "-" * 24, "-" * 24))
    for label, va, vb in [
        ("Company",    cr.name_a,                   cr.name_b),
        ("Tier",       cr.tier_a,                   cr.tier_b),
        ("Market Cap", _fmt_mcap(cr.market_cap_a),  _fmt_mcap(cr.market_cap_b)),
        ("Sector",     cr.sector_a,                 cr.sector_b),
        ("Industry",   cr.industry_a,               cr.industry_b),
    ]:
        lines.append(_profile_row(va, label, vb))
    lines.append("")

    # ── Sections ────────────────────────────────────────────────────
    for section in cr.sections:
        if section.winner == "a":
            badge = f"  [*] {cr.ticker_a} wins"
        elif section.winner == "b":
            badge = f"  {cr.ticker_b} wins [*]"
        else:
            badge = "  Tie"

        lines.append("-" * _W)
        lines.append(f"{section.name.upper()}{badge}".center(_W))
        lines.append("-" * _W)

        # Column header
        lines.append(_row(cr.ticker_a, "", "Metric", "", cr.ticker_b))
        lines.append(_sep())

        for m in section.metrics:
            # Winner prefix: [W] for winner, plain for loser
            if m.winner == "a":
                va = f"[W] {m.fmt_a}"
                vb = f"    {m.fmt_b}"
                al, ar = "<<<", ""
            elif m.winner == "b":
                va = f"    {m.fmt_a}"
                vb = f"[W] {m.fmt_b}"
                al, ar = "", ">>>"
            elif m.winner == "tie":
                va = f"    {m.fmt_a}"
                vb = f"    {m.fmt_b}"
                al, ar = "<=>", "<=>"
            else:
                va = f"    {m.fmt_a}"
                vb = f"    {m.fmt_b}"
                al, ar = "---", "---"

            lines.append(_row(va, al, m.label, ar, vb))

        # Section summary
        lines.append(_sep())
        sa = f"{section.wins_a}W {section.wins_b}L"
        sb = f"{section.wins_b}W {section.wins_a}L"
        lines.append(_row(sa, "", "SECTION RESULT", "", sb))
        lines.append("")

    # ── Scoreboard ──────────────────────────────────────────────────
    sc_s, sc_a, sc_w, sc_b = 22, 8, 22, 8
    def _sc_row(s: str, a: str, w: str, b: str) -> str:
        return f"    {s:<{sc_s}}  {a:^{sc_a}}  {w:^{sc_w}}  {b:^{sc_b}}"

    lines.append("-" * _W)
    lines.append("SECTION SCOREBOARD".center(_W))
    lines.append("-" * _W)
    lines.append(_sc_row("Section", cr.ticker_a, "Winner", cr.ticker_b))
    lines.append(_sc_row("-" * sc_s, "-" * sc_a, "-" * sc_w, "-" * sc_b))
    for s in cr.sections:
        if s.winner == "a":
            wt = f"<<< {cr.ticker_a}"
        elif s.winner == "b":
            wt = f"{cr.ticker_b} >>>"
        else:
            wt = "Tie"
        lines.append(_sc_row(s.name, f"{s.wins_a}W", wt, f"{s.wins_b}W"))
    lines.append("")

    # ── Verdict ─────────────────────────────────────────────────────
    lines.append("=" * _W)
    lines.append("[*] FINAL VERDICT [*]".center(_W))
    lines.append("=" * _W)

    sec_text = (
        f"Sections Won:  {cr.ticker_a} {cr.sections_won_a}"
        f"  :  {cr.sections_won_b} {cr.ticker_b}"
    )
    if cr.sections_tied:
        sec_text += f"   ({cr.sections_tied} tied)"
    lines.append(sec_text.center(_W))

    met_text = (
        f"Metrics Won:   {cr.ticker_a} {cr.total_wins_a}"
        f"  :  {cr.total_wins_b} {cr.ticker_b}"
    )
    if cr.total_ties:
        met_text += f"   ({cr.total_ties} tied)"
    lines.append(met_text.center(_W))
    lines.append("")

    if cr.overall_winner == "a":
        winner = f"OVERALL WINNER:  {cr.name_a} ({cr.ticker_a})"
    elif cr.overall_winner == "b":
        winner = f"OVERALL WINNER:  {cr.name_b} ({cr.ticker_b})"
    else:
        winner = "IT'S A TIE"
    lines.append(f">>> {winner} <<<".center(_W))
    lines.append("=" * _W)
    lines.append("")

    # ── Footer ──────────────────────────────────────────────────────
    lines.append(f"Generated by {APP_NAME} v{__version__} ({__year__})")
    lines.append(f"Developer: {DEVELOPER} | License: {LICENSE_NAME}")
    lines.append("")

    return "\n".join(lines)


# ===================================================================
# HTML export
# ===================================================================

def _esc(text: str) -> str:
    return _html.escape(str(text))


def _html_winner_class(winner: str, side: str) -> str:
    if winner == "na":
        return "na"
    if winner == "tie":
        return "tie"
    if winner == side:
        return "win"
    return "lose"


def export_html(cr: ComparisonResult) -> str:
    """Render comparison as a styled HTML document with white background."""
    parts: list[str] = []

    parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(cr.name_a)} vs {_esc(cr.name_b)} - Lynx Compare</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    background: #ffffff;
    color: #1a1a2e;
    line-height: 1.5;
    padding: 32px 24px;
    max-width: 960px;
    margin: 0 auto;
  }}
  h1 {{
    text-align: center;
    font-size: 1.6em;
    color: #16213e;
    margin-bottom: 4px;
  }}
  .subtitle {{
    text-align: center;
    color: #555;
    font-size: 0.95em;
    margin-bottom: 24px;
  }}
  .matchup {{
    text-align: center;
    font-size: 1.2em;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 20px;
  }}
  .matchup .vs {{ color: #c0392b; font-weight: 700; }}
  .ticker {{ color: #2980b9; }}
  .warning {{
    border-left: 4px solid #e74c3c;
    background: #fdf2f2;
    padding: 8px 14px;
    margin-bottom: 8px;
    font-size: 0.9em;
    color: #c0392b;
  }}
  .warning.industry {{ border-left-color: #e67e22; color: #d35400; background: #fef5ed; }}
  .warning.tier {{ border-left-color: #f1c40f; color: #9a7d0a; background: #fefce8; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
    font-size: 0.9em;
  }}
  th {{
    background: #f0f4f8;
    color: #16213e;
    padding: 8px 12px;
    text-align: center;
    border-bottom: 2px solid #d0d7de;
    font-weight: 600;
  }}
  td {{
    padding: 6px 12px;
    border-bottom: 1px solid #e8ecf0;
    text-align: center;
  }}
  tr:nth-child(even) {{ background: #f8fafb; }}
  tr:hover {{ background: #eef2f6; }}
  td.val-left {{ text-align: right; }}
  td.val-right {{ text-align: left; }}
  td.metric {{ font-weight: 500; color: #333; }}
  td.arrow {{ color: #888; font-size: 0.85em; }}
  .win {{ color: #27ae60; font-weight: 600; }}
  .lose {{ color: #95a5a6; }}
  .tie {{ color: #d4a017; font-weight: 500; }}
  .na {{ color: #bbb; }}
  .section-title {{
    background: #16213e;
    color: #fff;
    padding: 10px 16px;
    font-size: 1.05em;
    font-weight: 600;
    margin-top: 20px;
    border-radius: 4px 4px 0 0;
  }}
  .section-title .badge {{ float: right; font-size: 0.9em; }}
  .verdict-box {{
    border: 2px solid #27ae60;
    border-radius: 6px;
    padding: 20px;
    text-align: center;
    margin-top: 24px;
    background: #f0fff4;
  }}
  .verdict-box.is-tie {{
    border-color: #d4a017;
    background: #fffef0;
  }}
  .verdict-box h2 {{ font-size: 1.3em; margin-bottom: 10px; color: #16213e; }}
  .verdict-box .score {{ font-size: 0.95em; color: #444; margin-bottom: 4px; }}
  .verdict-box .winner {{
    font-size: 1.15em;
    font-weight: 700;
    color: #27ae60;
    margin-top: 12px;
  }}
  .verdict-box.is-tie .winner {{ color: #d4a017; }}
  .footer {{
    text-align: center;
    font-size: 0.8em;
    color: #999;
    margin-top: 32px;
    padding-top: 16px;
    border-top: 1px solid #e8ecf0;
  }}
  .check {{ color: #27ae60; }}
  .cross {{ color: #e74c3c; }}
  @media print {{
    body {{ padding: 12px; }}
    .section-title {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    tr:nth-child(even) {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  }}
</style>
</head>
<body>
<h1>Lynx Compare</h1>
<p class="subtitle">Fundamental Analysis Comparison Report</p>
<p class="matchup">
  {_esc(cr.name_a)} <span class="ticker">({_esc(cr.ticker_a)})</span>
  <span class="vs"> vs </span>
  {_esc(cr.name_b)} <span class="ticker">({_esc(cr.ticker_b)})</span>
</p>
""")

    # Warnings
    if cr.warnings:
        for w in cr.warnings:
            css_cls = w.level if w.level in ("industry", "tier") else ""
            parts.append(
                f'<div class="warning {css_cls}">'
                f'<strong>{_esc(w.level.upper())} MISMATCH:</strong> {_esc(w.message)}'
                f'</div>'
            )

    # Profile table
    parts.append('<div class="section-title">Company Profile</div>')
    parts.append('<table>')
    parts.append(f'<tr><th>{_esc(cr.ticker_a)}</th><th>Metric</th><th>{_esc(cr.ticker_b)}</th></tr>')
    profile_rows = [
        ("Company", cr.name_a, cr.name_b),
        ("Tier", cr.tier_a, cr.tier_b),
        ("Market Cap", _fmt_mcap(cr.market_cap_a), _fmt_mcap(cr.market_cap_b)),
        ("Sector", cr.sector_a, cr.sector_b),
        ("Industry", cr.industry_a, cr.industry_b),
    ]
    for label, va, vb in profile_rows:
        parts.append(
            f'<tr>'
            f'<td class="val-left">{_esc(va)}</td>'
            f'<td class="metric">{_esc(label)}</td>'
            f'<td class="val-right">{_esc(vb)}</td>'
            f'</tr>'
        )
    parts.append('</table>')

    # Sections
    for section in cr.sections:
        if section.winner == "a":
            badge = f"{TROPHY} {_esc(cr.ticker_a)} wins"
        elif section.winner == "b":
            badge = f"{_esc(cr.ticker_b)} wins {TROPHY}"
        else:
            badge = "Tie"

        parts.append(
            f'<div class="section-title">'
            f'{_esc(section.name.upper())}'
            f'<span class="badge">{badge}</span>'
            f'</div>'
        )
        parts.append('<table>')
        parts.append(
            f'<tr>'
            f'<th>{_esc(cr.ticker_a)}</th>'
            f'<th></th>'
            f'<th>Metric</th>'
            f'<th></th>'
            f'<th>{_esc(cr.ticker_b)}</th>'
            f'</tr>'
        )

        for m in section.metrics:
            cls_a = _html_winner_class(m.winner, "a")
            cls_b = _html_winner_class(m.winner, "b")
            prefix_a = f'<span class="check">{CHECK}</span> ' if m.winner == "a" else ""
            prefix_b = f'<span class="check">{CHECK}</span> ' if m.winner == "b" else ""
            arrow = _winner_arrow(m.winner) if m.winner in ("a", "b", "tie") else "---"

            arrow_l = arrow if m.winner in ("a", "tie") else ""
            arrow_r = arrow if m.winner in ("b", "tie") else ""
            if m.winner == "na":
                arrow_l = arrow_r = "---"

            parts.append(
                f'<tr>'
                f'<td class="val-left {cls_a}">{prefix_a}{_esc(m.fmt_a)}</td>'
                f'<td class="arrow">{arrow_l}</td>'
                f'<td class="metric">{_esc(m.label)}</td>'
                f'<td class="arrow">{arrow_r}</td>'
                f'<td class="val-right {cls_b}">{prefix_b}{_esc(m.fmt_b)}</td>'
                f'</tr>'
            )

        # Section summary
        sa = f"{section.wins_a}<span class='check'>{CHECK}</span> {section.wins_b}<span class='cross'>{CROSS}</span>"
        sb = f"{section.wins_b}<span class='check'>{CHECK}</span> {section.wins_a}<span class='cross'>{CROSS}</span>"
        parts.append(
            f'<tr style="font-weight:600; border-top:2px solid #d0d7de;">'
            f'<td class="val-left">{sa}</td>'
            f'<td></td>'
            f'<td class="metric">SECTION RESULT</td>'
            f'<td></td>'
            f'<td class="val-right">{sb}</td>'
            f'</tr>'
        )
        parts.append('</table>')

    # Scoreboard
    parts.append('<div class="section-title">Section Scoreboard</div>')
    parts.append('<table>')
    parts.append(
        f'<tr><th>Section</th><th>{_esc(cr.ticker_a)}</th>'
        f'<th>Winner</th><th>{_esc(cr.ticker_b)}</th></tr>'
    )
    for s in cr.sections:
        if s.winner == "a":
            wt = f'<span class="win">{ARROW_L} {_esc(cr.ticker_a)}</span>'
        elif s.winner == "b":
            wt = f'<span class="win">{_esc(cr.ticker_b)} {ARROW_R}</span>'
        else:
            wt = f'<span class="tie">Tie</span>'
        parts.append(
            f'<tr><td class="metric">{_esc(s.name)}</td>'
            f'<td>{s.wins_a}W</td>'
            f'<td>{wt}</td>'
            f'<td>{s.wins_b}W</td></tr>'
        )
    parts.append('</table>')

    # Verdict
    is_tie = cr.overall_winner == "tie"
    verdict_cls = "verdict-box is-tie" if is_tie else "verdict-box"
    parts.append(f'<div class="{verdict_cls}">')
    parts.append(f'<h2>{TROPHY} Final Verdict {TROPHY}</h2>')

    sec_text = f"Sections Won: {_esc(cr.ticker_a)} {cr.sections_won_a} : {cr.sections_won_b} {_esc(cr.ticker_b)}"
    if cr.sections_tied:
        sec_text += f" ({cr.sections_tied} tied)"
    parts.append(f'<p class="score">{sec_text}</p>')

    met_text = f"Metrics Won: {_esc(cr.ticker_a)} {cr.total_wins_a} : {cr.total_wins_b} {_esc(cr.ticker_b)}"
    if cr.total_ties:
        met_text += f" ({cr.total_ties} tied)"
    parts.append(f'<p class="score">{met_text}</p>')

    if cr.overall_winner == "a":
        winner_text = f"{CROWN} Overall Winner: {_esc(cr.name_a)} ({_esc(cr.ticker_a)}) {CROWN}"
    elif cr.overall_winner == "b":
        winner_text = f"{CROWN} Overall Winner: {_esc(cr.name_b)} ({_esc(cr.ticker_b)}) {CROWN}"
    else:
        winner_text = "It's a Tie"
    parts.append(f'<p class="winner">{winner_text}</p>')
    parts.append('</div>')

    # Footer
    parts.append(
        f'<div class="footer">'
        f'Generated by {_esc(APP_NAME)} v{_esc(__version__)} ({_esc(__year__)}) '
        f'| Developer: {_esc(DEVELOPER)} | License: {_esc(LICENSE_NAME)}'
        f'</div>'
    )

    parts.append('</body>\n</html>\n')
    return "\n".join(parts)


# ===================================================================
# PDF export (uses HTML-to-PDF)
# ===================================================================

def export_pdf(cr: ComparisonResult, output_path: str) -> str:
    """Export comparison as PDF.

    Tries ``weasyprint`` first, falls back to writing the HTML and
    converting via the system's ``wkhtmltopdf`` if available.  If
    neither is installed, writes the HTML with a ``.html`` extension
    next to *output_path* and raises an informative error.

    Returns the path of the written file.
    """
    html_content = export_html(cr)

    # Ensure parent directory exists
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Attempt weasyprint
    try:
        from weasyprint import HTML as WeasyprintHTML  # type: ignore[import-untyped]
        WeasyprintHTML(string=html_content).write_pdf(str(out))
        return output_path
    except ImportError:
        pass

    # Attempt wkhtmltopdf
    import shutil
    import subprocess
    import tempfile

    wk = shutil.which("wkhtmltopdf")
    if wk:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=".html", delete=False, mode="w", encoding="utf-8",
            ) as tmp:
                tmp.write(html_content)
                tmp_path = tmp.name
            subprocess.run(
                [wk, "--quiet", "--enable-local-file-access", tmp_path, output_path],
                check=True,
                capture_output=True,
            )
            return output_path
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    # Fallback: write HTML and inform user
    html_path = str(out.with_suffix(".html"))
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    raise RuntimeError(
        f"No PDF renderer found (install 'weasyprint' or 'wkhtmltopdf'). "
        f"HTML report saved to: {html_path}"
    )


# ===================================================================
# Default export path helpers
# ===================================================================

def _default_export_dir() -> Path:
    """Return a sensible default directory for exports.

    Prefers ``~/Documents/lynx-compare/``, falls back to ``~/lynx-compare/``.
    Creates the directory if it doesn't exist.
    """
    docs = Path.home() / "Documents"
    if docs.is_dir():
        export_dir = docs / "lynx-compare"
    else:
        export_dir = Path.home() / "lynx-compare"
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def default_export_path(cr: ComparisonResult, ext: str = ".html") -> str:
    """Build a default export file path for *cr*.

    The filename encodes the two tickers and a compact timestamp so
    successive exports don't overwrite each other::

        ~/Documents/lynx-compare/AAPL_vs_MSFT_20260415_143022.html
    """
    from datetime import datetime

    ext = ext if ext.startswith(".") else f".{ext}"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"{cr.ticker_a}_vs_{cr.ticker_b}_{ts}{ext}"
    return str(_default_export_dir() / name)


# ===================================================================
# Unified export dispatcher
# ===================================================================

def export_comparison(
    cr: ComparisonResult,
    output_path: str,
    fmt: str = "html",
) -> str:
    """Export comparison to the given format.

    Parameters
    ----------
    cr : ComparisonResult
        The comparison data.
    output_path : str
        Destination file path.
    fmt : str
        One of ``"html"``, ``"pdf"``, or ``"text"``.

    Returns
    -------
    str
        The path of the file written.
    """
    fmt = fmt.lower().strip()

    # Ensure parent directory exists for all formats
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if fmt == "pdf":
        return export_pdf(cr, output_path)

    if fmt in ("text", "txt", "plaintext"):
        content = export_text(cr)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path

    # Default: HTML
    content = export_html(cr)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path

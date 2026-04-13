"""Rich console display for comparison results.

Renders a polished three-column layout with clear visual hierarchy:
    Company A  |  Verdict (styled arrows)  |  Company B
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box

from lynx_compare.engine import ComparisonResult, SectionResult, Warning

console = Console()

# ---------------------------------------------------------------------------
# Unicode arrows and visual indicators
# ---------------------------------------------------------------------------
ARROW_WIN_LEFT = "\u25c0\u2501\u2501\u2501"    # ◀━━━
ARROW_WIN_RIGHT = "\u2501\u2501\u2501\u25b6"   # ━━━▶
ARROW_TIE = "\u25c0\u2550\u2550\u25b6"         # ◀══▶
ARROW_NA = "\u2500 \u2500 \u2500"              # ─ ─ ─
TROPHY = "\u2605"                               # ★
CROWN = "\u2654"                                # ♔
CHECK = "\u2714"                                # ✔
CROSS = "\u2718"                                # ✘
DOT = "\u2022"                                  # •
DIAMOND = "\u25c6"                              # ◆
WARN = "\u26a0"                                 # ⚠

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
C_WIN = "bold green"
C_LOSE = "dim white"
C_TIE = "bold yellow"
C_NA = "dim"
C_HEADER = "bold cyan"
C_METRIC = "white"
C_BORDER = "bright_blue"

# Warning styles — Rich supports "blink" on terminals that honour it.
C_WARN_SECTOR = "blink bold red"
C_WARN_INDUSTRY = "blink bold #ff8800"
C_WARN_TIER = "blink bold yellow"

_WARN_STYLES: dict[str, tuple[str, str]] = {
    "sector":   (C_WARN_SECTOR,   "red"),
    "industry": (C_WARN_INDUSTRY, "#ff8800"),
    "tier":     (C_WARN_TIER,     "yellow"),
}


def _fmt_money_short(val: float | None) -> str:
    if val is None:
        return "N/A"
    av = abs(val)
    neg = val < 0
    if av >= 1_000_000_000_000:
        s = f"${av / 1_000_000_000_000:,.2f}T"
    elif av >= 1_000_000_000:
        s = f"${av / 1_000_000_000:,.2f}B"
    elif av >= 1_000_000:
        s = f"${av / 1_000_000:,.2f}M"
    else:
        s = f"${av:,.0f}"
    return f"-{s}" if neg else s


# ---------------------------------------------------------------------------
# Value and arrow styling
# ---------------------------------------------------------------------------

def _styled_value(text: str, winner: str, side: str) -> Text:
    """Style a metric value.  Always uses a 2-char prefix so columns align."""
    if winner == "na":
        return Text(f"  {text}", style=C_NA)
    if winner == "tie":
        return Text(f"  {text}", style=C_TIE)
    if winner == side:
        return Text(f"{CHECK} {text}", style=C_WIN)
    return Text(f"  {text}", style=C_LOSE)


def _styled_arrow(winner: str) -> Text:
    if winner == "a":
        return Text(f" {ARROW_WIN_LEFT} ", style=C_WIN)
    if winner == "b":
        return Text(f" {ARROW_WIN_RIGHT} ", style=C_WIN)
    if winner == "tie":
        return Text(f" {ARROW_TIE} ", style=C_TIE)
    return Text(f" {ARROW_NA} ", style=C_NA)


def _section_arrow(winner: str, ticker_a: str, ticker_b: str) -> Text:
    t = Text()
    if winner == "a":
        t.append(f" {TROPHY} ", style="bold yellow")
        t.append(f"{ARROW_WIN_LEFT} {ticker_a} ", style=C_WIN)
    elif winner == "b":
        t.append(f" {ticker_b} {ARROW_WIN_RIGHT}", style=C_WIN)
        t.append(f" {TROPHY} ", style="bold yellow")
    else:
        t.append(f" {ARROW_TIE} TIE ", style=C_TIE)
    return t


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------

def _render_warnings(warnings: list[Warning]) -> None:
    """Render comparability warnings as compact banners.

    Only the ``LEVEL MISMATCH`` tags blink; the message text stays
    steady so it remains readable.
    """
    if not warnings:
        return
    for w in warnings:
        blink_style, border_color = _WARN_STYLES.get(
            w.level, (C_WARN_TIER, "yellow"),
        )
        # Steady colour = same hue without blink
        steady_style = blink_style.replace("blink ", "")
        tag = w.level.upper()
        # Build mixed-style text: blinking tags + steady message
        body = Text(justify="center")
        body.append(f"{WARN} {tag} MISMATCH ", style=blink_style)
        body.append(f" {w.message} ", style=steady_style)
        body.append(f" {tag} MISMATCH {WARN}", style=blink_style)
        console.print(
            Panel(
                body,
                border_style=border_color,
                padding=(0, 2),
                expand=True,
            )
        )


# ---------------------------------------------------------------------------
# Header banner
# ---------------------------------------------------------------------------

def _render_header(cr: ComparisonResult) -> None:
    inner = Text(justify="center")
    inner.append(f"\n{cr.name_a}", style="bold white")
    inner.append(f"  ({cr.ticker_a})", style="cyan")
    inner.append("     vs     ", style="bold yellow")
    inner.append(f"{cr.name_b}", style="bold white")
    inner.append(f"  ({cr.ticker_b})\n", style="cyan")

    panel = Panel(
        Align.center(inner),
        title=f"[bold cyan]{DIAMOND} LYNX COMPARE {DIAMOND}[/]",
        subtitle="[dim]Fundamental Analysis Comparison[/]",
        border_style="cyan",
        padding=(0, 4),
    )
    console.print(panel)


# ---------------------------------------------------------------------------
# Profile card
# ---------------------------------------------------------------------------

def _render_profile(cr: ComparisonResult) -> None:
    t = Table(
        box=box.DOUBLE_EDGE,
        border_style=C_BORDER,
        show_header=True,
        header_style=C_HEADER,
        expand=True,
        padding=(0, 3),
        title=f"[bold white]{DOT} Company Profile {DOT}[/]",
        title_style="bold",
    )
    t.add_column(cr.ticker_a, justify="right", ratio=3, style="bold white")
    t.add_column("", justify="center", ratio=2, style="bold cyan")
    t.add_column(cr.ticker_b, justify="left", ratio=3, style="bold white")

    t.add_row(cr.name_a, "Company", cr.name_b)
    t.add_row(cr.tier_a, "Tier", cr.tier_b)
    t.add_row(
        _fmt_money_short(cr.market_cap_a),
        "Market Cap",
        _fmt_money_short(cr.market_cap_b),
    )
    t.add_row(cr.sector_a, "Sector", cr.sector_b)
    t.add_row(cr.industry_a, "Industry", cr.industry_b)
    console.print(t)


# ---------------------------------------------------------------------------
# Section table
# ---------------------------------------------------------------------------

def _render_section(section: SectionResult, ticker_a: str, ticker_b: str) -> None:
    if section.winner == "a":
        badge = f"  [{C_WIN}]{TROPHY} {ticker_a} wins {ARROW_WIN_LEFT}[/]"
    elif section.winner == "b":
        badge = f"  [{C_WIN}]{ARROW_WIN_RIGHT} {ticker_b} wins {TROPHY}[/]"
    else:
        badge = f"  [{C_TIE}]{ARROW_TIE} Tie[/]"

    section_title = f"[bold white]{DOT} {section.name.upper()} {DOT}[/]{badge}"

    t = Table(
        title=section_title,
        box=box.HEAVY_HEAD,
        border_style=C_BORDER,
        show_header=True,
        header_style=C_HEADER,
        expand=True,
        padding=(0, 2),
        show_lines=False,
    )

    t.add_column(f"[bold]{ticker_a}[/]", justify="right", ratio=3, no_wrap=True)
    t.add_column("", justify="center", width=8, no_wrap=True)
    t.add_column("Metric", justify="center", ratio=3, no_wrap=True, style="bold")
    t.add_column("", justify="center", width=8, no_wrap=True)
    t.add_column(f"[bold]{ticker_b}[/]", justify="left", ratio=3, no_wrap=True)

    for m in section.metrics:
        val_a = _styled_value(m.fmt_a, m.winner, "a")
        val_b = _styled_value(m.fmt_b, m.winner, "b")
        arrow = _styled_arrow(m.winner)

        if m.winner == "a":
            t.add_row(val_a, arrow, Text(m.label, style=C_METRIC), Text(""), val_b)
        elif m.winner == "b":
            t.add_row(val_a, Text(""), Text(m.label, style=C_METRIC), arrow, val_b)
        elif m.winner == "tie":
            t.add_row(val_a, arrow, Text(m.label, style=C_METRIC), arrow, val_b)
        else:
            t.add_row(
                val_a,
                Text(f" {ARROW_NA} ", style=C_NA),
                Text(m.label, style="dim"),
                Text(f" {ARROW_NA} ", style=C_NA),
                val_b,
            )

    # Section summary row
    t.add_section()

    score_a = f"{section.wins_a}{CHECK}  {section.wins_b}{CROSS}  {section.ties}{DOT}"
    score_b = f"{section.wins_b}{CHECK}  {section.wins_a}{CROSS}  {section.ties}{DOT}"

    if section.winner == "a":
        t.add_row(
            Text(score_a, style=C_WIN),
            _section_arrow("a", ticker_a, ticker_b),
            Text("SECTION RESULT", style="bold"),
            Text(""),
            Text(score_b, style=C_LOSE),
        )
    elif section.winner == "b":
        t.add_row(
            Text(score_a, style=C_LOSE),
            Text(""),
            Text("SECTION RESULT", style="bold"),
            _section_arrow("b", ticker_a, ticker_b),
            Text(score_b, style=C_WIN),
        )
    else:
        t.add_row(
            Text(score_a, style=C_TIE),
            _section_arrow("tie", ticker_a, ticker_b),
            Text("SECTION RESULT", style="bold"),
            _section_arrow("tie", ticker_a, ticker_b),
            Text(score_b, style=C_TIE),
        )

    console.print(t)
    console.print()


# ---------------------------------------------------------------------------
# Scoreboard
# ---------------------------------------------------------------------------

def _render_scoreboard(cr: ComparisonResult) -> None:
    t = Table(
        box=box.SIMPLE_HEAVY,
        border_style="cyan",
        show_header=True,
        header_style=C_HEADER,
        expand=True,
        padding=(0, 2),
        title=f"[bold white]{DOT} Section Scoreboard {DOT}[/]",
    )
    t.add_column("Section", justify="center", ratio=2, style="bold")
    t.add_column(cr.ticker_a, justify="center", ratio=1)
    t.add_column("Winner", justify="center", ratio=1)
    t.add_column(cr.ticker_b, justify="center", ratio=1)

    for s in cr.sections:
        if s.winner == "a":
            winner_cell = Text(f"{ARROW_WIN_LEFT} {cr.ticker_a}", style=C_WIN)
            a_cell = Text(f"{s.wins_a}W", style=C_WIN)
            b_cell = Text(f"{s.wins_b}W", style=C_LOSE)
        elif s.winner == "b":
            winner_cell = Text(f"{cr.ticker_b} {ARROW_WIN_RIGHT}", style=C_WIN)
            a_cell = Text(f"{s.wins_a}W", style=C_LOSE)
            b_cell = Text(f"{s.wins_b}W", style=C_WIN)
        else:
            winner_cell = Text(f"{ARROW_TIE} Tie", style=C_TIE)
            a_cell = Text(f"{s.wins_a}W", style=C_TIE)
            b_cell = Text(f"{s.wins_b}W", style=C_TIE)
        t.add_row(s.name, a_cell, winner_cell, b_cell)

    console.print(t)
    console.print()


# ---------------------------------------------------------------------------
# Overall winner
# ---------------------------------------------------------------------------

def _render_overall(cr: ComparisonResult) -> None:
    sw_a = f"{cr.sections_won_a:>2}"
    sw_b = f"{cr.sections_won_b:<2}"
    mw_a = f"{cr.total_wins_a:>2}"
    mw_b = f"{cr.total_wins_b:<2}"

    lines = Text(justify="center")
    lines.append("\n")

    lines.append("Sections Won     ", style="bold")
    lines.append(f"{cr.ticker_a} ", style="cyan")
    lines.append(sw_a, style="bold white")
    lines.append("  :  ", style="dim")
    lines.append(sw_b, style="bold white")
    lines.append(f" {cr.ticker_b}", style="cyan")
    if cr.sections_tied:
        lines.append(f"   ({cr.sections_tied} tied)", style="yellow")
    lines.append("\n")

    lines.append("Metrics Won      ", style="bold")
    lines.append(f"{cr.ticker_a} ", style="cyan")
    lines.append(mw_a, style="bold white")
    lines.append("  :  ", style="dim")
    lines.append(mw_b, style="bold white")
    lines.append(f" {cr.ticker_b}", style="cyan")
    if cr.total_ties:
        lines.append(f"   ({cr.total_ties} tied)", style="yellow")
    lines.append("\n\n")

    if cr.overall_winner == "a":
        lines.append(
            f"{CROWN}  {ARROW_WIN_LEFT}  OVERALL WINNER:  "
            f"{cr.name_a} ({cr.ticker_a})  {CROWN}",
            style="bold green",
        )
        border = "green"
    elif cr.overall_winner == "b":
        lines.append(
            f"{CROWN}  OVERALL WINNER:  "
            f"{cr.name_b} ({cr.ticker_b})  {ARROW_WIN_RIGHT}  {CROWN}",
            style="bold green",
        )
        border = "green"
    else:
        lines.append(
            f"{ARROW_TIE}  IT'S A TIE  {ARROW_TIE}",
            style="bold yellow",
        )
        border = "yellow"

    lines.append("\n")

    panel = Panel(
        Align.center(lines),
        title=f"[bold white]{TROPHY} FINAL VERDICT {TROPHY}[/]",
        border_style=border,
        padding=(1, 4),
    )
    console.print(panel)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def display_comparison(cr: ComparisonResult) -> None:
    """Render the full comparison to the terminal."""
    console.print()
    _render_header(cr)
    console.print()

    # Show warnings right after header, before any data
    _render_warnings(cr.warnings)
    if cr.warnings:
        console.print()

    _render_profile(cr)
    console.print()

    for section in cr.sections:
        _render_section(section, cr.ticker_a, cr.ticker_b)

    _render_scoreboard(cr)
    _render_overall(cr)
    console.print()

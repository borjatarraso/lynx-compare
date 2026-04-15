"""Textual terminal UI for Lynx Compare."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
)

from lynx_compare.engine import ComparisonResult, SectionResult, Warning

# Unicode indicators (matching display.py)
TROPHY = "\u2605"       # ★
CHECK = "\u2714"        # ✔
CROSS = "\u2718"        # ✘
DOT = "\u2022"          # •
DIAMOND = "\u25c6"      # ◆
ARROW_L = "\u25c0\u2501\u2501\u2501"   # ◀━━━
ARROW_R = "\u2501\u2501\u2501\u25b6"   # ━━━▶
ARROW_TIE = "\u25c0\u2550\u2550\u25b6" # ◀══▶
ARROW_NA = "\u2500 \u2500 \u2500"      # ─ ─ ─
CROWN = "\u2654"        # ♔
WARN = "\u26a0"         # ⚠


# ---------------------------------------------------------------------------
# About modal dialog
# ---------------------------------------------------------------------------

class AboutModal(ModalScreen[None]):
    """Modal dialog showing application info, developer, and license.

    Only the license text scrolls; the rest of the dialog is fixed.
    """

    CSS = """
    AboutModal {
        align: center middle;
    }
    #about-dialog {
        width: 72;
        height: 34;
        border: round cyan;
        padding: 1 2;
        background: $surface;
    }
    #about-title {
        text-align: center;
        text-style: bold;
        color: cyan;
        margin-bottom: 1;
    }
    #about-version {
        text-align: center;
        color: $text-muted;
    }
    #about-desc {
        text-align: center;
        color: $text;
        margin-bottom: 1;
    }
    .about-heading {
        text-style: bold;
        color: cyan;
        margin-top: 1;
    }
    .about-text {
        color: $text;
        margin-left: 2;
    }
    .about-dim {
        color: $text-muted;
        margin-left: 2;
    }
    #about-license-scroll {
        margin: 1 2;
        padding: 0 1;
        border: round $primary-darken-2;
        height: 1fr;
    }
    #about-license-content {
        padding: 1 1;
        color: $text-muted;
    }
    #about-close-row {
        align: center middle;
        height: 3;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=True),
        Binding("enter", "close", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        from lynx_compare import __version__, __year__
        from lynx_compare.about import (
            APP_NAME, APP_DESCRIPTION, DEVELOPER, DEVELOPER_EMAIL,
            LICENSE_NAME, LICENSE_TEXT,
        )

        with Vertical(id="about-dialog"):
            yield Label(f"{DIAMOND} {APP_NAME} {DIAMOND}", id="about-title")
            yield Label(f"v{__version__}", id="about-version")
            yield Label(APP_DESCRIPTION, id="about-desc")

            yield Label("Developer", classes="about-heading")
            yield Label(f"  {DEVELOPER}", classes="about-text")
            yield Label(f"  {DEVELOPER_EMAIL}", classes="about-dim")

            yield Label("License", classes="about-heading")
            yield Label(f"  {LICENSE_NAME}", classes="about-text")

            with VerticalScroll(id="about-license-scroll"):
                yield Static(LICENSE_TEXT.strip(), id="about-license-content")

            with Horizontal(id="about-close-row"):
                yield Label("[bold cyan]Press Escape or Enter to close[/]")

    def action_close(self) -> None:
        self.dismiss(None)


# ---------------------------------------------------------------------------
# Easter egg modal
# ---------------------------------------------------------------------------

class EasterEggModal(ModalScreen[None]):
    """Hidden easter-egg modal with ASCII art."""

    CSS = """
    EasterEggModal {
        align: center middle;
    }
    #egg-dialog {
        width: 54;
        height: 24;
        border: round yellow;
        padding: 1 2;
        background: $surface;
    }
    #egg-title {
        text-align: center;
        text-style: bold;
        color: yellow;
        margin-bottom: 1;
    }
    #egg-art {
        color: green;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=True),
        Binding("enter", "close", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        from lynx_compare.about import easter_egg_text
        with Vertical(id="egg-dialog"):
            yield Label("You found the easter egg!", id="egg-title")
            yield Static(easter_egg_text().strip(), id="egg-art")

    def action_close(self) -> None:
        self.dismiss(None)


# ---------------------------------------------------------------------------
# Export modal dialog
# ---------------------------------------------------------------------------

class ExportModal(ModalScreen[str | None]):
    """Modal to choose export format and save location."""

    CSS = """
    ExportModal {
        align: center middle;
    }
    #export-dialog {
        width: 68;
        height: auto;
        border: round cyan;
        padding: 2 4;
        background: $surface;
    }
    #export-dialog Label {
        margin-bottom: 1;
    }
    #export-title {
        text-align: center;
        text-style: bold;
        color: cyan;
        margin-bottom: 1;
    }
    #export-matchup {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    .export-heading {
        text-style: bold;
        color: cyan;
        margin-top: 1;
    }
    .export-fmt-row {
        margin-left: 2;
    }
    .export-hint {
        color: $text-muted;
        margin-left: 4;
    }
    #export-path-label {
        margin-top: 1;
        text-style: bold;
        color: cyan;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    def __init__(self, cr: ComparisonResult) -> None:
        super().__init__()
        self._cr = cr

    def compose(self) -> ComposeResult:
        from lynx_compare.export import default_export_path
        default_path = default_export_path(self._cr, ".html")

        with Vertical(id="export-dialog"):
            yield Label(
                f"{DIAMOND} Export Comparison Report {DIAMOND}",
                id="export-title",
            )
            yield Label(
                f"{self._cr.name_a} ({self._cr.ticker_a}) vs "
                f"{self._cr.name_b} ({self._cr.ticker_b})",
                id="export-matchup",
            )

            yield Label("Format  [dim](change extension to switch)[/]", classes="export-heading")
            yield Label("[bold].html[/]  Styled HTML document", classes="export-fmt-row")
            yield Label("[bold].pdf [/]  Printable PDF", classes="export-fmt-row")
            yield Label("[bold].txt [/]  Plain text", classes="export-fmt-row")

            yield Label("Save to:", id="export-path-label")
            yield Input(
                value=default_path,
                placeholder=default_path,
                id="export-path",
            )
            yield Label(
                "[dim]Edit the path or change extension, then press Enter[/]",
            )
            yield Label(
                "[dim]Press Escape to cancel[/]",
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        val = event.value.strip()
        if val:
            self.dismiss(val)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ---------------------------------------------------------------------------
# Timeout modal dialog
# ---------------------------------------------------------------------------

class TimeoutModal(ModalScreen[int | None]):
    """Modal dialog to change the analysis timeout."""

    CSS = """
    TimeoutModal {
        align: center middle;
    }
    #timeout-dialog {
        width: 50;
        height: auto;
        border: round cyan;
        padding: 2 4;
        background: $surface;
    }
    #timeout-dialog Label {
        margin-bottom: 1;
    }
    #timeout-dialog Input {
        margin-bottom: 1;
    }
    #timeout-title {
        text-align: center;
        text-style: bold;
        color: cyan;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    def __init__(self, current: int) -> None:
        super().__init__()
        self.current = current

    def compose(self) -> ComposeResult:
        with Vertical(id="timeout-dialog"):
            yield Label("Change Timeout", id="timeout-title")
            yield Label(f"Current timeout: {self.current}s")
            yield Input(
                value=str(self.current),
                placeholder="seconds",
                id="new-timeout",
                type="integer",
            )
            yield Label("[dim]Press Enter to apply, Escape to cancel[/]")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            val = int(event.value.strip())
            if val > 0:
                self.dismiss(val)
                return
        except ValueError:
            pass
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ---------------------------------------------------------------------------
# Input screen
# ---------------------------------------------------------------------------

class InputScreen(Screen):
    """Screen that collects two company identifiers."""

    BINDINGS = [
        Binding("ctrl+q", "app.quit", "Quit", show=True),
        Binding("ctrl+t", "change_timeout", "Timeout", show=True),
        Binding("ctrl+a", "show_about", "About", show=True),
        Binding("tab", "focus_next", "Next", show=True),
        Binding("shift+tab", "focus_previous", "Prev", show=True),
    ]

    CSS = """
    InputScreen {
        align: center middle;
    }
    #input-box {
        width: 76;
        height: auto;
        border: round cyan;
        padding: 2 4;
    }
    #input-box Label {
        margin-bottom: 1;
    }
    #input-box Input {
        margin-bottom: 1;
    }
    #title {
        text-align: center;
        text-style: bold;
        color: cyan;
        margin-bottom: 1;
    }
    #subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    #timeout-row {
        height: 3;
        margin-top: 1;
    }
    #timeout-label {
        margin-top: 1;
        width: auto;
    }
    #timeout-input {
        width: 12;
    }
    #button-row {
        height: 3;
        margin-top: 1;
        align: center middle;
    }
    #compare-btn {
        margin-right: 2;
    }
    #status-label {
        margin-top: 2;
        text-align: center;
        height: 3;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="input-box"):
            yield Label(f"{DIAMOND} LYNX COMPARE {DIAMOND}", id="title")
            yield Label("Enter two companies to compare", id="subtitle")
            yield Input(
                placeholder="First company (ticker / ISIN / name)",
                id="company_a",
            )
            yield Input(
                placeholder="Second company (ticker / ISIN / name)",
                id="company_b",
            )
            with Horizontal(id="timeout-row"):
                yield Label("Timeout (seconds): ", id="timeout-label")
                yield Input(
                    value="30",
                    placeholder="30",
                    id="timeout-input",
                    type="integer",
                )
            with Horizontal(id="button-row"):
                yield Button(
                    f"{DIAMOND} Compare", variant="primary", id="compare-btn",
                )
                yield Button("Clear", variant="default", id="clear-btn")
            yield Label("", id="status-label")
        yield Footer()

    def on_mount(self) -> None:
        """Sync timeout input with CLI args after app is ready."""
        app: LynxCompareApp = self.app  # type: ignore[assignment]
        timeout = getattr(app.cli_args, "timeout", 30)
        self.query_one("#timeout-input", Input).value = str(timeout)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "company_a":
            self.query_one("#company_b", Input).focus()
            return
        if event.input.id == "company_b":
            self.query_one("#timeout-input", Input).focus()
            return
        if event.input.id == "timeout-input":
            self.query_one("#compare-btn", Button).focus()
            return

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "compare-btn":
            self._start_comparison()
        elif event.button.id == "clear-btn":
            self.query_one("#company_a", Input).value = ""
            self.query_one("#company_b", Input).value = ""
            self.query_one("#status-label", Label).update("")
            self.query_one("#company_a", Input).focus()

    def action_change_timeout(self) -> None:
        app: LynxCompareApp = self.app  # type: ignore[assignment]
        current = getattr(app.cli_args, "timeout", 30)
        self.app.push_screen(TimeoutModal(current), self._on_timeout_result)

    def _on_timeout_result(self, val: int | None) -> None:
        if val is not None and val > 0:
            app: LynxCompareApp = self.app  # type: ignore[assignment]
            app.cli_args.timeout = val
            self.query_one("#timeout-input", Input).value = str(val)

    def action_show_about(self) -> None:
        self.app.push_screen(AboutModal())

    # Spinner frames for the analysing animation
    _SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    _DOTS = [".", "..", "...", "....", "...", ".."]

    def _start_comparison(self) -> None:
        a = self.query_one("#company_a", Input).value.strip()
        b = self.query_one("#company_b", Input).value.strip()
        if not a or not b:
            self.query_one("#status-label", Label).update(
                "[bold red]Please enter both companies.[/]"
            )
            return

        # Check easter egg
        from lynx_compare.about import check_easter_egg
        if check_easter_egg(a) or check_easter_egg(b):
            self.app.push_screen(EasterEggModal())
            return

        # Update timeout from input
        try:
            tv = int(self.query_one("#timeout-input", Input).value.strip())
            if tv > 0:
                self.app.cli_args.timeout = tv  # type: ignore[union-attr]
        except (ValueError, AttributeError):
            pass

        # Disable buttons during analysis
        self.query_one("#compare-btn", Button).disabled = True
        self.query_one("#clear-btn", Button).disabled = True

        # Start animated status
        self._anim_frame = 0
        self._anim_phase = f"Analysing {a}"
        timeout_s = getattr(self.app.cli_args, "timeout", 30)  # type: ignore[union-attr]
        self._anim_suffix = f"  [dim](timeout {timeout_s}s)[/]"
        self._anim_timer = self.set_interval(0.12, self._animate_status)

        self.app.call_after_refresh(self._run_comparison, a, b)

    def _animate_status(self) -> None:
        """Cycle spinner and dots on the status label."""
        try:
            label = self.query_one("#status-label", Label)
        except Exception:
            return  # widget not mounted yet or already removed
        spinner = self._SPINNER[self._anim_frame % len(self._SPINNER)]
        dots = self._DOTS[self._anim_frame // 2 % len(self._DOTS)]
        # Build a bar of small blocks that pulses
        bar_len = 20
        pos = self._anim_frame % (bar_len * 2)
        if pos >= bar_len:
            pos = bar_len * 2 - pos
        bar = (
            "[dim cyan]" + "━" * pos + "[/]"
            "[bold cyan]◆[/]"
            "[dim cyan]" + "━" * (bar_len - pos) + "[/]"
        )
        label.update(
            f"{bar}\n"
            f"[bold yellow]{spinner} {self._anim_phase}{dots}[/]"
            f"{self._anim_suffix}"
        )
        self._anim_frame += 1

    def _stop_animation(self) -> None:
        """Stop the status animation and re-enable buttons."""
        if hasattr(self, "_anim_timer") and self._anim_timer is not None:
            self._anim_timer.stop()
            self._anim_timer = None
        try:
            self.query_one("#compare-btn", Button).disabled = False
            self.query_one("#clear-btn", Button).disabled = False
        except Exception:
            pass

    def _run_comparison(self, company_a: str, company_b: str) -> None:
        app: LynxCompareApp = self.app  # type: ignore[assignment]
        try:
            from lynx_compare.cli import _run_analysis, AnalysisTimeoutError
            from lynx_compare.engine import compare

            self._anim_phase = f"Analysing {company_a}"
            report_a = _run_analysis(company_a, app.cli_args)

            self._anim_phase = f"Analysing {company_b}"
            report_b = _run_analysis(company_b, app.cli_args)

            self._anim_phase = "Comparing"
            result = compare(report_a, report_b)

            self._stop_animation()
            app.push_screen(ResultScreen(result))

        except AnalysisTimeoutError as exc:
            self._stop_animation()
            timeout = getattr(app.cli_args, "timeout", 30)
            self.query_one("#status-label", Label).update(
                f"[bold red]{WARN} Timeout:[/] {exc}\n"
                f"[dim]Tip: increase timeout (currently {timeout}s)[/]"
            )
        except Exception as exc:
            self._stop_animation()
            self.query_one("#status-label", Label).update(
                f"[bold red]Error: {exc}[/]"
            )


# ---------------------------------------------------------------------------
# Helpers for consistent value formatting in DataTable cells
# ---------------------------------------------------------------------------

def _cell_value(fmt: str, winner: str, side: str) -> str:
    if winner == "na" or winner == "tie":
        return f"  {fmt}"
    if winner == side:
        return f"{CHECK} {fmt}"
    return f"  {fmt}"


def _cell_arrow_l(winner: str) -> str:
    if winner == "a":
        return ARROW_L
    if winner == "tie":
        return ARROW_TIE
    if winner == "na":
        return ARROW_NA
    return ""


def _cell_arrow_r(winner: str) -> str:
    if winner == "b":
        return ARROW_R
    if winner == "tie":
        return ARROW_TIE
    if winner == "na":
        return ARROW_NA
    return ""


# ---------------------------------------------------------------------------
# Warning style mapping
# ---------------------------------------------------------------------------

_TUI_WARN_STYLES: dict[str, tuple[str, str]] = {
    "sector":   ("bold blink red", "red"),
    "industry": ("bold blink #ff8800", "#ff8800"),
    "tier":     ("bold blink yellow", "yellow"),
}


def _build_warnings(warnings: list[Warning]) -> list[Static]:
    """Build compact warning Static widgets for the TUI.

    Only the LEVEL MISMATCH tags blink; the message text stays steady.
    """
    widgets: list[Static] = []
    for w in warnings:
        blink_style, border_color = _TUI_WARN_STYLES.get(
            w.level, ("bold yellow", "yellow"),
        )
        steady_style = blink_style.replace("blink ", "")
        tag = w.level.upper()
        markup = (
            f"[{blink_style}]{WARN} {tag} MISMATCH[/]"
            f"  [{steady_style}]{w.message}[/]  "
            f"[{blink_style}]{tag} MISMATCH {WARN}[/]"
        )
        widgets.append(Static(markup, classes=f"warning-{w.level}"))
    return widgets


# ---------------------------------------------------------------------------
# Result screen
# ---------------------------------------------------------------------------

class ResultScreen(Screen):
    """Screen that displays comparison results."""

    BINDINGS = [
        Binding("ctrl+q", "app.quit", "Quit", show=True),
        Binding("ctrl+t", "change_timeout", "Timeout", show=True),
        Binding("ctrl+a", "show_about", "About", show=True),
        Binding("ctrl+e", "export", "Export", show=True),
        Binding("q", "pop_screen", "Back", show=True),
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("tab", "focus_next", "Next Section", show=True),
        Binding("shift+tab", "focus_previous", "Prev Section", show=True),
        Binding("up", "scroll_up", "Scroll Up", show=False),
        Binding("down", "scroll_down", "Scroll Down", show=False),
    ]

    CSS = """
    ResultScreen {
        overflow-y: auto;
    }
    #result-scroll {
        height: 1fr;
    }
    .verdict-panel {
        text-align: center;
        padding: 1 2;
        margin: 1 2;
        border: round green;
    }
    .verdict-panel-tie {
        text-align: center;
        padding: 1 2;
        margin: 1 2;
        border: round yellow;
    }
    .header-banner {
        text-align: center;
        padding: 1;
        background: $primary-darken-3;
        color: cyan;
        text-style: bold;
    }
    .spacer {
        height: 1;
    }
    .warning-sector {
        text-align: center;
        padding: 0 2;
        margin: 0 1;
        border: heavy red;
        background: $error 10%;
    }
    .warning-industry {
        text-align: center;
        padding: 0 2;
        margin: 0 1;
        border: heavy #ff8800;
        background: $warning 10%;
    }
    .warning-tier {
        text-align: center;
        padding: 0 2;
        margin: 0 1;
        border: heavy yellow;
    }
    """

    def __init__(self, result: ComparisonResult) -> None:
        super().__init__()
        self.result = result

    def compose(self) -> ComposeResult:
        cr = self.result
        yield Header(show_clock=True)

        with VerticalScroll(id="result-scroll"):
            # Banner
            yield Static(
                f"[bold cyan]{DIAMOND} LYNX COMPARE {DIAMOND}[/]  --  "
                f"[bold white]{cr.name_a}[/] ([cyan]{cr.ticker_a}[/])"
                f"  [bold yellow]vs[/]  "
                f"[bold white]{cr.name_b}[/] ([cyan]{cr.ticker_b}[/])",
                classes="header-banner",
            )

            # Warnings
            for widget in _build_warnings(cr.warnings):
                yield widget

            # Profile
            yield self._build_profile_table()
            yield Static("", classes="spacer")

            # Sections
            for section in cr.sections:
                yield self._build_section_table(section)
                yield Static("", classes="spacer")

            # Scoreboard + verdict
            yield self._build_scoreboard()
            yield Static("", classes="spacer")
            yield self._build_verdict()

        yield Footer()

    def action_change_timeout(self) -> None:
        app: LynxCompareApp = self.app  # type: ignore[assignment]
        current = getattr(app.cli_args, "timeout", 30)
        self.app.push_screen(TimeoutModal(current), self._on_timeout_result)

    def _on_timeout_result(self, val: int | None) -> None:
        if val is not None and val > 0:
            app: LynxCompareApp = self.app  # type: ignore[assignment]
            app.cli_args.timeout = val

    def action_show_about(self) -> None:
        self.app.push_screen(AboutModal())

    def action_export(self) -> None:
        self.app.push_screen(ExportModal(self.result), self._on_export_result)

    def _on_export_result(self, path: str | None) -> None:
        if path is None:
            return
        import os
        ext = os.path.splitext(path)[1].lower()
        fmt_map = {".html": "html", ".htm": "html", ".pdf": "pdf", ".txt": "text"}
        fmt = fmt_map.get(ext, "html")
        if not ext:
            path += ".html"
            fmt = "html"
        try:
            from lynx_compare.export import export_comparison
            result_path = export_comparison(self.result, path, fmt)
            self.notify(f"Exported to {result_path}", title="Export")
        except Exception as exc:
            self.notify(str(exc), title="Export Error", severity="error")

    def action_scroll_up(self) -> None:
        self.query_one("#result-scroll", VerticalScroll).scroll_up()

    def action_scroll_down(self) -> None:
        self.query_one("#result-scroll", VerticalScroll).scroll_down()

    def _build_profile_table(self) -> DataTable:
        cr = self.result
        # Use the same 5-column layout as section tables so columns align
        dt = DataTable(zebra_stripes=True)
        dt.add_column(cr.ticker_a, width=24)
        dt.add_column("", width=8)
        dt.add_column(f"{DOT} PROFILE {DOT}", width=40)
        dt.add_column("", width=8)
        dt.add_column(cr.ticker_b, width=24)

        from lynx_compare.engine import fmt_value
        dt.add_row(cr.name_a, "", "Company", "", cr.name_b)
        dt.add_row(cr.tier_a, "", "Tier", "", cr.tier_b)
        dt.add_row(
            fmt_value("market_cap", cr.market_cap_a),
            "", "Market Cap", "",
            fmt_value("market_cap", cr.market_cap_b),
        )
        dt.add_row(cr.sector_a, "", "Sector", "", cr.sector_b)
        dt.add_row(cr.industry_a, "", "Industry", "", cr.industry_b)
        return dt

    def _build_section_table(self, section: SectionResult) -> DataTable:
        cr = self.result

        if section.winner == "a":
            badge = f"  {TROPHY} {cr.ticker_a} wins {ARROW_L}"
        elif section.winner == "b":
            badge = f"  {ARROW_R} {cr.ticker_b} wins {TROPHY}"
        else:
            badge = f"  {ARROW_TIE} Tie"

        dt = DataTable(zebra_stripes=True)
        dt.add_column(cr.ticker_a, width=24)
        dt.add_column("", width=8)
        dt.add_column(f"{DOT} {section.name.upper()}{badge}", width=40)
        dt.add_column("", width=8)
        dt.add_column(cr.ticker_b, width=24)

        for m in section.metrics:
            va = _cell_value(m.fmt_a, m.winner, "a")
            vb = _cell_value(m.fmt_b, m.winner, "b")
            al = _cell_arrow_l(m.winner)
            ar = _cell_arrow_r(m.winner)
            dt.add_row(va, al, m.label, ar, vb)

        # Summary row
        sa = f"{section.wins_a}{CHECK} {section.wins_b}{CROSS} {section.ties}{DOT}"
        sb = f"{section.wins_b}{CHECK} {section.wins_a}{CROSS} {section.ties}{DOT}"
        if section.winner == "a":
            al_s, ar_s = f"{TROPHY} {ARROW_L}", ""
        elif section.winner == "b":
            al_s, ar_s = "", f"{ARROW_R} {TROPHY}"
        else:
            al_s, ar_s = ARROW_TIE, ARROW_TIE
        dt.add_row(sa, al_s, "SECTION RESULT", ar_s, sb)

        return dt

    def _build_scoreboard(self) -> DataTable:
        cr = self.result
        # Same 5-column layout as Profile and Section tables
        dt = DataTable(zebra_stripes=True)
        dt.add_column(cr.ticker_a, width=24)
        dt.add_column("", width=8)
        dt.add_column(f"{DOT} SECTION SCOREBOARD {DOT}", width=40)
        dt.add_column("", width=8)
        dt.add_column(cr.ticker_b, width=24)

        for s in cr.sections:
            if s.winner == "a":
                va = f"{s.wins_a}W (WINNER)"
                vb = f"{s.wins_b}W"
                al, ar = ARROW_L, ""
            elif s.winner == "b":
                va = f"{s.wins_a}W"
                vb = f"{s.wins_b}W (WINNER)"
                al, ar = "", ARROW_R
            else:
                va = f"{s.wins_a}W"
                vb = f"{s.wins_b}W"
                al, ar = ARROW_TIE, ARROW_TIE
            dt.add_row(va, al, s.name, ar, vb)
        return dt

    def _build_verdict(self) -> Static:
        cr = self.result

        sw_a = f"{cr.sections_won_a:>2}"
        sw_b = f"{cr.sections_won_b:<2}"
        mw_a = f"{cr.total_wins_a:>2}"
        mw_b = f"{cr.total_wins_b:<2}"

        lines = []
        sec_line = (
            f"Sections Won     {cr.ticker_a} {sw_a}  :  {sw_b} {cr.ticker_b}"
        )
        if cr.sections_tied:
            sec_line += f"   ({cr.sections_tied} tied)"
        lines.append(sec_line)

        met_line = (
            f"Metrics Won      {cr.ticker_a} {mw_a}  :  {mw_b} {cr.ticker_b}"
        )
        if cr.total_ties:
            met_line += f"   ({cr.total_ties} tied)"
        lines.append(met_line)

        if cr.overall_winner == "a":
            lines.append(
                f"\n[bold green]{CROWN}  {ARROW_L}  OVERALL WINNER:  "
                f"{cr.name_a} ({cr.ticker_a})  {CROWN}[/]"
            )
            css_class = "verdict-panel"
        elif cr.overall_winner == "b":
            lines.append(
                f"\n[bold green]{CROWN}  OVERALL WINNER:  "
                f"{cr.name_b} ({cr.ticker_b})  {ARROW_R}  {CROWN}[/]"
            )
            css_class = "verdict-panel"
        else:
            lines.append(f"\n[bold yellow]{ARROW_TIE}  IT'S A TIE  {ARROW_TIE}[/]")
            css_class = "verdict-panel-tie"

        return Static("\n".join(lines), classes=css_class)

    def action_pop_screen(self) -> None:
        self.app.pop_screen()


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

class LynxCompareApp(App):
    """Textual application for Lynx Compare."""

    TITLE = "Lynx Compare"
    SUB_TITLE = "Fundamental Analysis Comparison"

    CSS = """
    Screen {
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+t", "change_timeout", "Timeout", show=True),
        Binding("ctrl+a", "show_about", "About", show=True),
        Binding("tab", "focus_next", "Next", show=True),
        Binding("shift+tab", "focus_previous", "Prev", show=True),
    ]

    def __init__(self, cli_args) -> None:
        super().__init__()
        self.cli_args = cli_args

    def on_mount(self) -> None:
        self.push_screen(InputScreen())

    def action_change_timeout(self) -> None:
        current = getattr(self.cli_args, "timeout", 30)
        self.push_screen(TimeoutModal(current), self._on_timeout_result)

    def _on_timeout_result(self, val: int | None) -> None:
        if val is not None and val > 0:
            self.cli_args.timeout = val

    def action_show_about(self) -> None:
        self.push_screen(AboutModal())


def run_tui(args) -> None:
    """Launch the Textual TUI."""
    app = LynxCompareApp(cli_args=args)
    app.run()

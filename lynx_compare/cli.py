"""Command-line interface for Lynx Compare."""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

from lynx_compare import __author__, __version__, __year__, SUITE_LABEL

DEFAULT_TIMEOUT = 30


def _ticker_completer(prefix, **kw):
    """Dynamic completer that returns cached tickers from the core storage."""
    try:
        from lynx_investor_core.storage import list_cached_tickers
        items = list_cached_tickers() or []
        return [t["ticker"] for t in items if t["ticker"].startswith(prefix.upper())]
    except Exception:
        return []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lynx-compare",
        description=(
            "Lynx Compare — Side-by-side fundamental analysis comparison.\n"
            "Compare two publicly traded companies across valuation,\n"
            "profitability, solvency, growth, efficiency, moat, and\n"
            "intrinsic value metrics.\n\n"
            "One of --production-mode (-p) or --testing-mode (-t) is required."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  lynx-compare -p AAPL MSFT                CLI comparison (default)\n"
            "  lynx-compare -p -i                       Interactive mode\n"
            "  lynx-compare -p -tui                     Textual UI mode\n"
            "  lynx-compare -t AAPL GOOGL               Testing mode (fresh data)\n"
            "  lynx-compare -p AAPL MSFT --refresh      Force fresh data\n"
            "  lynx-compare -p AAPL MSFT --no-reports   Skip SEC filings\n"
            "  lynx-compare -p AAPL MSFT --timeout 60   Set 60s timeout per company\n"
            "  lynx-compare -p -x                       Graphical UI mode\n"
            "  lynx-compare --about                     Show developer & license info\n"
            "  lynx-compare -p AAPL MSFT --export r.html   Export to HTML\n"
            "  lynx-compare -p AAPL MSFT --export r.pdf    Export to PDF\n"
            "  lynx-compare -p AAPL MSFT --export r.txt    Export to text\n"
        ),
    )

    # --- Required: execution mode (unless --about) ---
    run_mode = parser.add_mutually_exclusive_group(required=False)
    run_mode.add_argument(
        "-p", "--production-mode",
        action="store_const",
        const="production",
        dest="run_mode",
        help="Production mode: use cached data from lynx-fa data/ directory",
    )
    run_mode.add_argument(
        "-t", "--testing-mode",
        action="store_const",
        const="testing",
        dest="run_mode",
        help="Testing mode: always fetch fresh data (uses data_test/)",
    )

    # --- Positional: two companies ---
    companies_arg = parser.add_argument(
        "companies",
        nargs="*",
        metavar="COMPANY",
        help="Two company identifiers (ticker, ISIN, or name) to compare",
    )
    companies_arg.completer = _ticker_completer

    # --- Interface mode ---
    ui_mode = parser.add_mutually_exclusive_group()
    ui_mode.add_argument(
        "-i", "--interactive-mode",
        action="store_true",
        dest="interactive",
        help="Launch interactive prompt mode",
    )
    ui_mode.add_argument(
        "-tui", "--textual-ui",
        action="store_true",
        dest="tui",
        help="Launch the Textual terminal UI",
    )
    ui_mode.add_argument(
        "-x", "--gui",
        action="store_true",
        dest="gui",
        help="Launch the graphical user interface",
    )

    def _positive_timeout(value: str) -> int:
        try:
            n = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{value} is not an integer")
        if n < 5:
            raise argparse.ArgumentTypeError(
                f"timeout must be >= 5 seconds (got {n})",
            )
        return n

    # --- Data options ---
    parser.add_argument(
        "--timeout",
        type=_positive_timeout,
        default=DEFAULT_TIMEOUT,
        metavar="SECS",
        help=f"Timeout in seconds per company analysis (default: {DEFAULT_TIMEOUT}, min: 5)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force fresh data download (ignore cache)",
    )
    parser.add_argument(
        "--no-reports",
        action="store_true",
        help="Skip fetching/downloading SEC filings",
    )
    parser.add_argument(
        "--no-news",
        action="store_true",
        help="Skip fetching news articles",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output during analysis",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}  |  {SUITE_LABEL}  ({__year__}) by {__author__}",
    )

    # --- About & Export ---
    parser.add_argument(
        "--about",
        action="store_true",
        help="Show developer and license information",
    )
    parser.add_argument(
        "--export",
        metavar="FILE",
        help="Export comparison to file (format from extension: .html, .pdf, .txt)",
    )

    return parser


class AnalysisTimeoutError(Exception):
    """Raised when a company analysis exceeds the configured timeout."""


def _run_analysis(identifier: str, args) -> object:
    """Run lynx-fa analysis for a single company with a timeout guard."""
    from lynx.core.analyzer import run_full_analysis
    from lynx.core.storage import is_testing

    refresh = args.refresh or is_testing()

    def _do_analysis():
        return run_full_analysis(
            identifier=identifier,
            download_reports=not args.no_reports,
            download_news=not args.no_news,
            verbose=args.verbose,
            refresh=refresh,
        )

    timeout = getattr(args, "timeout", DEFAULT_TIMEOUT)

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_do_analysis)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeout:
            raise AnalysisTimeoutError(
                f"Analysis for '{identifier}' timed out after {timeout}s. "
                f"The ticker/ISIN may be invalid or the network is slow.\n"
                f"  Tip: use --timeout {timeout * 2} to increase the limit."
            )


def run_cli() -> None:
    """Parse arguments and dispatch to the appropriate mode."""
    parser = build_parser()

    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass  # argcomplete optional at runtime

    args = parser.parse_args()

    from rich.console import Console
    errc = Console(stderr=True)

    # --- About (standalone, no mode required) ---
    if args.about:
        from rich.panel import Panel
        from lynx_compare.about import about_text
        console = Console()
        console.print()
        console.print(Panel(
            about_text(),
            title="[bold cyan]About Lynx Compare[/]",
            border_style="cyan",
            padding=(1, 2),
        ))
        console.print()
        return

    # --- Easter egg: if either company is a trigger word ---
    from lynx_compare.about import check_easter_egg, easter_egg_text
    if args.companies:
        for c in args.companies:
            if check_easter_egg(c):
                from rich.panel import Panel
                console = Console()
                console.print()
                console.print(Panel(
                    f"[green]{easter_egg_text()}[/]",
                    title="[bold yellow]You found it![/]",
                    border_style="yellow",
                    padding=(0, 2),
                ))
                console.print()
                return

    # --- Require run mode for actual analysis ---
    if args.run_mode is None:
        errc.print(
            "[bold red]Error:[/] One of --production-mode (-p) or "
            "--testing-mode (-t) is required.\n"
            "  Use --about for app info without a mode."
        )
        sys.exit(1)

    # --- Activate storage mode FIRST ---
    from lynx.core.storage import set_mode
    set_mode(args.run_mode)

    mode_label = (
        "[bold green]PRODUCTION[/]"
        if args.run_mode == "production"
        else "[bold yellow]TESTING[/]"
    )
    errc.print(f"Mode: {mode_label}  |  Timeout: {args.timeout}s per company")

    # --- Interface dispatch ---
    if args.interactive:
        from lynx_compare.interactive import run_interactive
        run_interactive(args)
        return

    if args.tui:
        from lynx_compare.tui.app import run_tui
        run_tui(args)
        return

    if args.gui:
        from lynx_compare.gui.app import run_gui
        run_gui(args)
        return

    # --- Non-interactive CLI mode ---
    if len(args.companies) != 2:
        errc.print(
            "[bold red]Error:[/] Provide exactly two company identifiers.\n"
            "  Usage: lynx-compare -p AAPL MSFT\n"
            "  Or use -i for interactive mode."
        )
        sys.exit(1)

    company_a, company_b = args.companies

    from rich.progress import Progress, SpinnerColumn, TextColumn

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=errc,
            transient=True,
        ) as progress:
            task = progress.add_task(
                f"Analysing {company_a} (timeout {args.timeout}s)...",
                total=None,
            )
            report_a = _run_analysis(company_a, args)

            progress.update(
                task,
                description=f"Analysing {company_b} (timeout {args.timeout}s)...",
            )
            report_b = _run_analysis(company_b, args)

            progress.update(task, description="Comparing...")

        from lynx_compare.engine import compare
        from lynx_compare.display import display_comparison

        result = compare(report_a, report_b)
        display_comparison(result)

        # --- Export if requested ---
        if args.export:
            import os
            from lynx_compare.export import export_comparison, default_export_path

            path = args.export
            # Allow bare format keywords: --export html, --export pdf, --export text
            fmt_shortcuts = {"html": ".html", "pdf": ".pdf", "text": ".txt", "txt": ".txt"}
            if path in fmt_shortcuts:
                ext = fmt_shortcuts[path]
                path = default_export_path(result, ext)
                fmt = {".html": "html", ".pdf": "pdf", ".txt": "text"}.get(ext, "html")
            else:
                ext = os.path.splitext(path)[1].lower()
                fmt_map = {".html": "html", ".htm": "html", ".pdf": "pdf", ".txt": "text"}
                fmt = fmt_map.get(ext, "html")
                if not ext:
                    path = default_export_path(result, ".html")
                    fmt = "html"
            try:
                result_path = export_comparison(result, path, fmt)
                errc.print(f"[green]Exported to: {result_path}[/]")
            except RuntimeError as exc:
                errc.print(f"[yellow]{exc}[/]")
            except Exception as exc:
                errc.print(f"[bold red]Export error:[/] {exc}")

    except AnalysisTimeoutError as e:
        errc.print(f"[bold red]Timeout:[/] {e}")
        sys.exit(1)
    except ValueError as e:
        errc.print(f"[bold red]Error:[/] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(130)

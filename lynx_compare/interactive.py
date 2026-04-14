"""Interactive prompt mode for Lynx Compare."""

from __future__ import annotations

from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
errc = Console(stderr=True)


def run_interactive(args) -> None:
    """Run the interactive comparison loop."""
    from lynx.core.storage import is_testing
    from lynx_compare.cli import _run_analysis, AnalysisTimeoutError

    console.print()
    console.print("[bold cyan]LYNX COMPARE[/] -- Interactive Mode")
    console.print(
        f"[dim]Timeout: {args.timeout}s per company[/]"
    )
    console.print()
    console.print("[dim]Commands:[/]")
    console.print("[dim]  Ctrl+C   Abort current / quit[/]")
    console.print("[dim]  quit     Exit the program[/]")
    console.print("[dim]  timeout  Change the timeout (e.g. 'timeout 60')[/]")
    console.print("[dim]  about    Show application info[/]")
    console.print("[dim]  export   Export last comparison (e.g. 'export report.html')[/]")
    console.print()

    last_result = None

    while True:
        try:
            company_a = Prompt.ask(
                "[bold]Enter first company[/] (ticker, ISIN, or name)",
                console=console,
            ).strip()
            if company_a.lower() in ("quit", "exit", "q"):
                break
            if not company_a:
                continue
            # Handle inline commands
            if company_a.lower().startswith("timeout"):
                _handle_timeout_cmd(company_a, args)
                continue
            if company_a.lower() == "about":
                _show_about()
                continue
            if company_a.lower().startswith("export"):
                _handle_export_cmd(company_a, last_result)
                continue

            # Easter egg check
            from lynx_compare.about import check_easter_egg
            if check_easter_egg(company_a):
                _show_easter_egg()
                continue

            company_b = Prompt.ask(
                "[bold]Enter second company[/] (ticker, ISIN, or name)",
                console=console,
            ).strip()
            if company_b.lower() in ("quit", "exit", "q"):
                break
            if not company_b:
                continue
            if company_b.lower().startswith("timeout"):
                _handle_timeout_cmd(company_b, args)
                continue
            if company_b.lower() == "about":
                _show_about()
                continue
            if company_b.lower().startswith("export"):
                _handle_export_cmd(company_b, last_result)
                continue
            if check_easter_egg(company_b):
                _show_easter_egg()
                continue

            console.print()

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
            last_result = result
            display_comparison(result)

            console.print()
            console.print(
                "[dim]Type two more tickers to compare again, "
                "'timeout N' to change timeout, 'about' for info, "
                "'export <file>' to save, or 'quit' to exit.[/]"
            )
            console.rule(style="dim")
            console.print()

        except AnalysisTimeoutError as e:
            console.print(f"[bold red]Timeout:[/] {e}")
            try:
                new_timeout = IntPrompt.ask(
                    "[bold]Increase timeout?[/] Enter new seconds (or 0 to skip)",
                    default=0,
                    console=console,
                )
                if new_timeout > 0:
                    args.timeout = new_timeout
                    console.print(f"[green]Timeout updated to {new_timeout}s[/]")
            except (KeyboardInterrupt, EOFError):
                pass
            console.print()
        except ValueError as e:
            console.print(f"[bold red]Error:[/] {e}")
            console.print()
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted.[/]")
            break

    console.print("[dim]Goodbye.[/]")


def _handle_timeout_cmd(cmd: str, args) -> None:
    """Parse 'timeout N' command and update args."""
    parts = cmd.strip().split()
    if len(parts) == 2:
        try:
            val = int(parts[1])
            if val > 0:
                args.timeout = val
                console.print(f"[green]Timeout updated to {val}s[/]")
                return
        except ValueError:
            pass
    console.print(
        f"[dim]Current timeout: {args.timeout}s. "
        f"Usage: timeout 60[/]"
    )


def _show_about() -> None:
    """Display About information."""
    from rich.panel import Panel
    from lynx_compare.about import about_text
    console.print()
    console.print(Panel(
        about_text(),
        title="[bold cyan]About Lynx Compare[/]",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()


def _show_easter_egg() -> None:
    """Display the easter egg."""
    from rich.panel import Panel
    from lynx_compare.about import easter_egg_text
    console.print()
    console.print(Panel(
        f"[green]{easter_egg_text()}[/]",
        title="[bold yellow]You found it![/]",
        border_style="yellow",
        padding=(0, 2),
    ))
    console.print()


def _handle_export_cmd(cmd: str, last_result) -> None:
    """Parse 'export [filename]' command and export.

    If no filename is given, uses a smart default path under
    ``~/Documents/lynx-compare/``.  If only an extension is given
    (e.g. ``export .pdf``), the default name is used with that format.
    """
    if last_result is None:
        console.print(
            "[yellow]No comparison results to export. "
            "Run a comparison first.[/]"
        )
        return

    import os
    from lynx_compare.export import export_comparison, default_export_path

    parts = cmd.strip().split(maxsplit=1)
    arg = parts[1].strip() if len(parts) >= 2 else ""

    # No argument or just a bare format name -> use smart default
    fmt_shortcuts = {"html": ".html", "pdf": ".pdf", "text": ".txt", "txt": ".txt"}
    if not arg:
        # Bare "export" -> prompt with choices
        from lynx_compare.export import _default_export_dir
        console.print()
        console.print("[bold cyan]Export Comparison Report[/]")
        console.print(f"[dim]Default location: {_default_export_dir()}[/]")
        console.print()
        console.print("  [bold]1[/]  HTML  [dim]Styled document for browser[/]")
        console.print("  [bold]2[/]  PDF   [dim]Printable document[/]")
        console.print("  [bold]3[/]  Text  [dim]Plain text file[/]")
        console.print()
        choice = Prompt.ask(
            "[bold]Choose format[/]",
            choices=["1", "2", "3", "html", "pdf", "text", "txt"],
            default="1",
            console=console,
        ).strip()
        ext_map = {
            "1": ".html", "2": ".pdf", "3": ".txt",
            "html": ".html", "pdf": ".pdf", "text": ".txt", "txt": ".txt",
        }
        ext = ext_map.get(choice, ".html")
        path = default_export_path(last_result, ext)
        fmt_map = {".html": "html", ".pdf": "pdf", ".txt": "text"}
        fmt = fmt_map[ext]
    elif arg in fmt_shortcuts:
        # "export pdf" -> default path with that format
        ext = fmt_shortcuts[arg]
        path = default_export_path(last_result, ext)
        fmt_map = {".html": "html", ".pdf": "pdf", ".txt": "text"}
        fmt = fmt_map[ext]
    elif arg.startswith(".") and arg in (".html", ".pdf", ".txt"):
        # "export .pdf" -> default path with that extension
        path = default_export_path(last_result, arg)
        fmt_map = {".html": "html", ".pdf": "pdf", ".txt": "text"}
        fmt = fmt_map[arg]
    else:
        # Explicit path given
        path = arg
        ext = os.path.splitext(path)[1].lower()
        fmt_map = {".html": "html", ".htm": "html", ".pdf": "pdf", ".txt": "text"}
        fmt = fmt_map.get(ext, "html")
        if not ext:
            path += ".html"
            fmt = "html"

    try:
        result_path = export_comparison(last_result, path, fmt)
        console.print(f"[green]Exported to: {result_path}[/]")
    except RuntimeError as exc:
        console.print(f"[yellow]{exc}[/]")
    except Exception as exc:
        console.print(f"[bold red]Export error:[/] {exc}")

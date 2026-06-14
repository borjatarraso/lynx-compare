# PYTHON_ARGCOMPLETE_OK
"""Entry point for lynx-compare."""

from lynx_compare.interfaces.cli import run_cli


def main() -> None:
    run_cli()


if __name__ == "__main__":
    main()

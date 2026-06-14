"""lynx_compare.interfaces — user-facing entry points.

This subpackage wires the core/render layers to humans and clients:
argument parsing and command dispatch (:mod:`~lynx_compare.interfaces.cli`),
the REPL (:mod:`~lynx_compare.interfaces.interactive`), and the Flask REST
API (:mod:`~lynx_compare.interfaces.server`). The graphical frontends live in
the sibling :mod:`lynx_compare.tui` and :mod:`lynx_compare.gui` packages,
which ``cli`` launches on demand.
"""

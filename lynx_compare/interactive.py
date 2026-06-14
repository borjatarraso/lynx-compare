"""Backward-compatibility shim.

The interactive REPL moved to :mod:`lynx_compare.interfaces.interactive`.
This module re-exports it so the historical ``lynx_compare.interactive``
import path keeps working. New code should import from
:mod:`lynx_compare.interfaces.interactive` directly.
"""

import sys as _sys

from lynx_compare.interfaces import interactive as _impl

_sys.modules[__name__] = _impl

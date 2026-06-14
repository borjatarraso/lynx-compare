"""Backward-compatibility shim.

The CLI moved to :mod:`lynx_compare.interfaces.cli`. This module re-exports
it so the historical ``lynx_compare.cli`` import path keeps working
(including private helpers such as ``_run_analysis``). New code should import
from :mod:`lynx_compare.interfaces.cli` directly.
"""

import sys as _sys

from lynx_compare.interfaces import cli as _impl

_sys.modules[__name__] = _impl

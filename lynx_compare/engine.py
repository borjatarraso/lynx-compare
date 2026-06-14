"""Backward-compatibility shim.

The comparison engine moved to :mod:`lynx_compare.core.engine`. This module
re-exports it so the historical ``lynx_compare.engine`` import path keeps
working (including private names such as ``_INFO_ONLY``). New code should
import from :mod:`lynx_compare.core.engine` directly.
"""

import sys as _sys

from lynx_compare.core import engine as _impl

_sys.modules[__name__] = _impl

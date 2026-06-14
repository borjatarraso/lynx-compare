"""Backward-compatibility shim.

The N-way comparison logic moved to :mod:`lynx_compare.core.multi`. This
module re-exports it so the historical ``lynx_compare.multi`` import path
keeps working. New code should import from :mod:`lynx_compare.core.multi`
directly.
"""

import sys as _sys

from lynx_compare.core import multi as _impl

_sys.modules[__name__] = _impl

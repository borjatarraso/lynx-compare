"""Backward-compatibility shim.

The metadata/about constants moved to :mod:`lynx_compare.core.about`. This
module re-exports them so the historical ``lynx_compare.about`` import path
keeps working. New code should import from :mod:`lynx_compare.core.about`
directly.
"""

import sys as _sys

from lynx_compare.core import about as _impl

_sys.modules[__name__] = _impl

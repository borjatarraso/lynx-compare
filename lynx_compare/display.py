"""Backward-compatibility shim.

The Rich console renderer moved to :mod:`lynx_compare.render.display`. This
module re-exports it so the historical ``lynx_compare.display`` import path
keeps working. New code should import from :mod:`lynx_compare.render.display`
directly.
"""

import sys as _sys

from lynx_compare.render import display as _impl

_sys.modules[__name__] = _impl

"""Backward-compatibility shim.

The exporters moved to :mod:`lynx_compare.render.export`. This module
re-exports them so the historical ``lynx_compare.export`` import path keeps
working (including private names such as ``_default_export_dir``). New code
should import from :mod:`lynx_compare.render.export` directly.
"""

import sys as _sys

from lynx_compare.render import export as _impl

_sys.modules[__name__] = _impl

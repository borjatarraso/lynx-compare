"""Backward-compatibility shim.

The Flask REST server moved to :mod:`lynx_compare.interfaces.server`. This
module re-exports it so the historical ``lynx_compare.server`` import path
(used by the ``lynx-compare-server`` console script and the test suite) keeps
working. New code should import from :mod:`lynx_compare.interfaces.server`
directly.
"""

import sys as _sys

from lynx_compare.interfaces import server as _impl

_sys.modules[__name__] = _impl

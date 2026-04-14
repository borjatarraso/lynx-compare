"""About information and easter egg for Lynx Compare."""

from __future__ import annotations

from lynx_compare import __author__, __version__, __year__

# ---------------------------------------------------------------------------
# Developer and license metadata
# ---------------------------------------------------------------------------

APP_NAME = "Lynx Compare"
APP_DESCRIPTION = "Side-by-side fundamental analysis comparison tool"
DEVELOPER = "Borja Tarraso"
DEVELOPER_EMAIL = "borja.tarraso@member.fsf.org"
LICENSE_NAME = "BSD 3-Clause License"
LICENSE_SPDX = "BSD-3-Clause"

LICENSE_TEXT = f"""\
BSD 3-Clause License

Copyright (c) {__year__}, {DEVELOPER} <{DEVELOPER_EMAIL}>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


def about_lines() -> list[str]:
    """Return About information as a list of plain-text lines."""
    return [
        f"{APP_NAME} v{__version__}",
        f"{APP_DESCRIPTION}",
        "",
        f"Developer:  {DEVELOPER}",
        f"Email:      {DEVELOPER_EMAIL}",
        f"Year:       {__year__}",
        f"License:    {LICENSE_NAME}",
        "",
        LICENSE_TEXT.rstrip(),
    ]


def about_text() -> str:
    """Return About information as a single string."""
    return "\n".join(about_lines())


# ---------------------------------------------------------------------------
# Easter egg
# ---------------------------------------------------------------------------

EASTER_EGG_TRIGGERS = {"lynx", "meow", "paw"}

EASTER_EGG_ART = r"""
        /\_/\
       ( o.o )
        > ^ <       _
       /|   |\     | |   _   _ _ __ __  __
      (_|   |_)    | |  | | | | '_ \\ \/ /
        |   |      | |__| |_| | | | |>  <
        |___|      |_____\__, |_| |_/_/\_\
       /     \           |___/
      / LYNX  \    Fundamental Analysis
     /  COMPARE\   Comparison Tool
    /___________\
       |  |  |     "The silent hunter of
       |  |  |      undervalued stocks."
      _|  |  |_
     (_/  |  \_)   -- Happy investing! --
          |
"""


def check_easter_egg(text: str) -> bool:
    """Return True if *text* matches an easter-egg trigger."""
    return text.strip().lower() in EASTER_EGG_TRIGGERS


def easter_egg_text() -> str:
    """Return the easter-egg ASCII art."""
    return EASTER_EGG_ART

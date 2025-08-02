from __future__ import annotations


import os
import pathlib
from typing import Final


def ansi(code):
    return f"\u001b[{code}m"


_APPDATA_FARETEK: Final[str] = os.getenv('LOCALAPPDATA') + "\\faretek"
_APPDATA_FARETEK_INFLATE: Final[str] = _APPDATA_FARETEK + "\\inflate"
APPDATA_FARETEK_PKGS: Final[pathlib.Path] = pathlib.Path(_APPDATA_FARETEK_INFLATE + "\\pkgs")

GITHUB_REPO: Final[str] = "no github link rn"
ERROR_MSG: Final[str] = f"{ansi(31)}-9999 aura 💀{ansi(0)}\nFile an issue on github: {GITHUB_REPO}"

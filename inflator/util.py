from __future__ import annotations


import os
import pathlib
from typing import Final


def ansi(code):
    return f"\u001b[{code}m"


_APPDATA_FARETEK: Final[str] = os.getenv('LOCALAPPDATA') + "\\faretek"
_APPDATA_FARETEK_INFLATE: Final[str] = _APPDATA_FARETEK + "\\inflate"
APPDATA_FARETEK_PKGS: Final[pathlib.Path] = pathlib.Path(_APPDATA_FARETEK_INFLATE + "\\pkgs")
APPDATA_FARETEK_ZIPAREA: Final[pathlib.Path] = pathlib.Path(_APPDATA_FARETEK_INFLATE + "\\ziparea")

GITHUB_REPO: Final[str] = "https://github.com/FAReTek1/inflator"
AURA: Final[str] = "-9999 aura 💀"
ERROR_MSG: Final[str] = f"{ansi(31)}{AURA}{ansi(0)}\nFile an issue on github: {GITHUB_REPO}"

from __future__ import annotations


import os
import pathlib
from typing import Final


def ansi(code):
    return f"\u001b[{code}m"


APPDATA_FARETEK: Final[pathlib.Path] = pathlib.Path(os.getenv('LOCALAPPDATA')) / "faretek"
APPDATA_FARETEK_INFLATE: Final[pathlib.Path] = APPDATA_FARETEK / "inflate"
APPDATA_FARETEK_PKGS: Final[pathlib.Path] = APPDATA_FARETEK_INFLATE / "pkgs"
APPDATA_FARETEK_ZIPAREA: Final[pathlib.Path] = APPDATA_FARETEK_INFLATE / "ziparea"

GITHUB_REPO: Final[str] = "https://github.com/FAReTek1/inflator"
AURA: Final[str] = "-9999 aura 💀"
ERROR_MSG: Final[str] = f"{ansi(31)}{AURA}{ansi(0)}\nFile an issue on github: {GITHUB_REPO}"

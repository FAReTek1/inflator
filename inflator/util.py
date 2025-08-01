import os
from typing import Final


def ansi(code):
    return f"\u001b[{code}m"


APPDATA_FARETEK: Final[str] = os.getenv('LOCALAPPDATA') + "\\faretek"
APPDATA_FARETEK_INFLATE: Final[str] = APPDATA_FARETEK + "\\inflate"
APPDATA_FARETEK_PKGS: Final[str] = APPDATA_FARETEK_INFLATE + "\\pkgs"

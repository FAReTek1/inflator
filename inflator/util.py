import os
from typing import Final


def ansi(code):
    return f"\u001b[{code}m"


APPDATA_FARETEK: Final[str] = os.getenv('LOCALAPPDATA') + "\\faretek"

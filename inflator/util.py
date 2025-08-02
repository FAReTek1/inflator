from __future__ import annotations

import os
import pathlib
import shutil
import stat

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


def rmtree(path, ignore_errors=False):
    # https://stackoverflow.com/questions/58878089/how-to-remove-git-repository-in-python-on-windows
    for root, dirs, files in os.walk(path):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IRWXU)
        for file in files:
            os.chmod(os.path.join(root, file), stat.S_IRWXU)

    shutil.rmtree(path, ignore_errors=ignore_errors)

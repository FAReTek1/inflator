import argparse
import os

from enum import Enum, auto
from typing import Final

from inflator.util import ansi


class Modes(Enum):
    INSTALL = auto()
    SYNC = auto()


GITHUB_REPO: Final[str] = "no github link rn"
ERROR_MSG: Final[str] = f"{ansi(31)}-9999 aura 💀{ansi(0)}\nFile an issue on github: {GITHUB_REPO}"


def main():
    def get_args():
        parser = argparse.ArgumentParser(
            prog="inflate",
            description="Manage libraries for use in goboscript",
            epilog=f':)'
        )

        parser.add_argument("-i", "--input", action="store", dest="input")
        parser.add_argument("install", nargs="?")
        parser.add_argument("pargs", nargs="*")

        return parser.parse_args()

    def resolve_args():
        nonlocal args, mode
        if args.install:
            mode = Modes.INSTALL

    args = get_args()
    mode = Modes.SYNC
    resolve_args()

    match mode:
        case Modes.INSTALL:
            pkgs = args.pargs

            from inflator.install import install
            install(pkgs)

        case Modes.SYNC:
            print("Synchronizing libraries")
            raise Exception(f"Not implemented\n{ERROR_MSG}")
        case _:
            print(f"Uh, how did we get here?\n{mode=}, {args.__dict__=}\n{ERROR_MSG}")

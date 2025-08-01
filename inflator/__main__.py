import argparse
import os

from enum import Enum, auto
from typing import Final


class Modes(Enum):
    INSTALL = auto()
    SYNC = auto()


def ansi(code):
    return f"\u001b[{code}m"


ERROR_MSG: Final[str] = f"{ansi(31)}-9999 aura 💀{ansi(0)}"


def main():
    def get_args():
        parser = argparse.ArgumentParser(
            prog="inflate",
            description="Manage libraries for use in goboscript",
            epilog=f':)'
        )

        parser.add_argument("-i", "--input", action="store", dest="input")
        parser.add_argument("install", nargs="?")

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
            print("Installing libraries")
        case Modes.SYNC:
            print("Synchronizing libraries")
        case _:
            print(f"Uh, how did we get here?\n{mode=}, {args.__dict__=}\n{ERROR_MSG}")

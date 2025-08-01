import argparse
import os

from enum import Enum, auto
from typing import Final

from inflator import __version__
from inflator.util import ansi


GITHUB_REPO: Final[str] = "no github link rn"
ERROR_MSG: Final[str] = f"{ansi(31)}-9999 aura 💀{ansi(0)}\nFile an issue on github: {GITHUB_REPO}"


def main():
    parser = argparse.ArgumentParser(
        prog="inflate",
        description="Manage libraries for use in goboscript",
        epilog=f':)'
    )
    subparsers = parser.add_subparsers(dest="command")

    parser.add_argument("-i", "--input", action="store")
    parser.add_argument("-V", "--version", action="store_true", dest="V")

    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("parg", nargs="?")
    install_parser.add_argument("-V", "--version", nargs="?", dest="install_version")

    # args, _ = parser.parse_known_args()
    args = parser.parse_args()

    match args.command:
        case "install":
            from inflator.install import install
            install(args.parg, args.install_version)

        case _:
            if args.V:
                print(f"Inflate {__version__}")
            else:
                print("Synchronizing libraries")
                print(f"{args.command=} {args.__dict__=}")

                print(f"Not implemented\n{ERROR_MSG}")

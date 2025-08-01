import argparse
import tomllib

from typing import Final

from inflator import __version__
from inflator.install import install
from inflator.gstoml import parse_gstoml, parse_iftoml
from inflator.util import ansi
from inflator.install import search_for_package

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
    install_parser.add_argument("-U", "--upgrade", action="store_true", dest="install_upgrade")
    install_parser.add_argument("-r", "--requirements", nargs="?", dest="install_requirements",
                                help="Path to inflator.toml/goboscript.toml file")

    find_parser = subparsers.add_parser("find", help="locate a package with a name/version/creator. "
                                                     "Can also be used to list out installed pkgs")
    find_parser.add_argument("name", nargs="?")  # , dest="find_name")
    find_parser.add_argument("-V", "--version", nargs="?", dest="find_version")
    find_parser.add_argument("-U", "--username", nargs="?", dest="find_username")

    # args, _ = parser.parse_known_args()
    args = parser.parse_args()

    match args.command:
        case "install":
            if args.install_requirements:
                with open(args.install_requirements, "rb") as f:
                    if f.name.endswith("goboscript.toml"):
                        _, deps = parse_gstoml(tomllib.load(f))
                    elif f.name.endswith("inflator.toml"):
                        _, deps = parse_iftoml(tomllib.load(f))
                    else:
                        raise ValueError(f"File {f.name!r} is not goboscript.toml or inflator.toml\n{ERROR_MSG}")

                for dep, raw in deps.items():
                    install(raw["raw"], raw["version"])
            else:
                install(args.parg, args.install_version, upgrade=args.install_upgrade)

        case "find":
            print('', *search_for_package(args.name, args.find_version, args.find_username), sep='\n')

        case _:
            if args.V:
                print(f"Inflate {__version__}")
            else:
                print("Synchronizing libraries")
                print(f"{args.command=} {args.__dict__=}")

                print(f"Not implemented\n{ERROR_MSG}")

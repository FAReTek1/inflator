from __future__ import annotations

import argparse
import pathlib
import pprint
import time
import tomllib
import logging

from datetime import datetime

from inflator import __version__
from inflator.install import install
from inflator.parse import parse_gstoml, parse_iftoml
from inflator.package import search_for_package
from inflator.sync import sync
from inflator.util import ERROR_MSG


def main():
    __file_dir__ = pathlib.Path(*pathlib.Path(__file__).parts[:-2])
    log_folder = __file_dir__ / "logs"

    logging.basicConfig(filename=log_folder / f"{time.time()}.log", level=logging.INFO)

    logging.info(f"init: {datetime.now()}")

    parser = argparse.ArgumentParser(
        prog="inflate",
        description="Manage libraries for use in goboscript.",
        epilog="When called with no args: Sync libraries in the current directory."
    )
    subparsers = parser.add_subparsers(dest="command")

    parser.add_argument("-i", "--input", action="store", help="Set input directory for syncing. Default is cwd")
    parser.add_argument("-V", "--version", action="store_true", dest="V", help="Get inflator version number")
    parser.add_argument("-L", "--log-folder", action="store_true", dest="L", help="Get log folder")

    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("parg", nargs="?", help="Package to install")
    install_parser.add_argument("-V", "--version", nargs="?", dest="install_version",
                                help="Version of package to install. Defaults to newest version")
    install_parser.add_argument("-e", "--editable", action="store_true", dest="install_editable",
                                help="For local packages. Whether to install the package as a symlink so that "
                                     "when you edit it, changes are directly made to your installation")
    install_parser.add_argument("-U", "--upgrade", action="store_true", dest="install_upgrade",
                                help="Whether to force overwrite packages "
                                     "instead of just installing ones that dont exist")
    install_parser.add_argument("-r", "--requirements", nargs="?", dest="install_requirements",
                                help="Path to inflator.toml/goboscript.toml file")

    find_parser = subparsers.add_parser("find", help="Locate a package with a name/version/creator. "
                                                     "Can also be used to list out installed pkgs. "
                                                     "It is globbed.")
    find_parser.add_argument("name", nargs="?", help="Name of package/repository")  # , dest="find_name")
    find_parser.add_argument("-V", "--version", nargs="?", dest="find_version",
                             help="Version of package")
    find_parser.add_argument("-U", "--username", nargs="?", dest="find_username",
                             help="Username of creator of package")

    parse_parser = subparsers.add_parser("parse", help="Parse gstoml or iftoml file")
    parse_parser.add_argument("name", nargs="?", help="Path to goboscript.toml or inflator.toml")  # , dest="find_name")

    # args, _ = parser.parse_known_args()
    args = parser.parse_args()

    match args.command:
        case "install":
            if args.install_requirements:
                with open(args.install_requirements, "rb") as f:
                    if f.name.endswith("goboscript.toml"):
                        deps = parse_gstoml(tomllib.load(f)).deps
                    elif f.name.endswith("inflator.toml"):
                        deps = parse_iftoml(tomllib.load(f)).deps
                    else:
                        raise ValueError(f"File {f.name!r} is not goboscript.toml or inflator.toml\n{ERROR_MSG}")

                for dep in deps:
                    dep.install(editable=args.install_editable, upgrade=args.install_upgrade)
            else:
                install(args.parg, args.install_version, upgrade=args.install_upgrade, editable=args.install_editable)

        case "find":
            pks = search_for_package(args.find_username, args.name, args.find_version)
            for pk in pks:
                print(pk.name)

        case "parse":
            with open(args.name, "rb") as f:
                if f.name.endswith("goboscript.toml"):
                    data = parse_gstoml(tomllib.load(f))
                else:
                    data = parse_iftoml(tomllib.load(f))
                pprint.pp(data)

        case _:
            if args.V:
                print(f"Inflate {__version__}")
            elif args.L:
                print(f"{log_folder=}")
            else:

                if args.input:
                    cwd = pathlib.Path(args.input)
                else:
                    cwd = pathlib.Path.cwd()

                sync(cwd)

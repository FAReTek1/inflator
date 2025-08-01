import logging
import os
import re

from typing import Self, Optional
from dataclasses import dataclass
from enum import Enum, auto

from furl import furl

from inflator import gstoml

APPDATA = os.getenv('LOCALAPPDATA') + "\\faretek"


def install(raw: str):
    pkg = Package.parse(raw)
    pkg.install()


class PackageTypes(Enum):
    LOCAL = auto()
    GIT = auto()


@dataclass
class Package:
    raw: str
    type: PackageTypes

    name: Optional[str] = None

    @classmethod
    def parse(cls, raw: str) -> Self:
        f = furl(raw)

        ptype = PackageTypes.LOCAL
        if f.host is not None:
            ptype = PackageTypes.GIT

        return cls(
            raw=raw,
            type=ptype,
        )

    def __str__(self):
        return self.raw

    def install(self):
        print(f"- Installing {self}")

        def install_local():
            print("\tLocal Package")
            print("\tFetching goboscript.toml/inflate.toml")
            print(f"\tInstalling into {APPDATA}")

        def install_git():
            print("\tGit Package")
            # https://api.github.com/repos/{usernae}/{reponame}/tags
            # https://api.github.com/repos/{username}/{reponame}/zipball/refs/tags/v{tagname}

        match self.type:
            case PackageTypes.LOCAL:
                install_local()
            case PackageTypes.GIT:
                install_git()

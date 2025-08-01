import os

from typing import Self, Optional
from dataclasses import dataclass
from enum import Enum, auto

from furl import furl

APPDATA = os.getenv('LOCALAPPDATA') + "\\faretek"


def install(pkgs: list[str]):
    print(f"INSTALL: {pkgs}")

    for pkg in pkgs:
        Package.parse(pkg).install()


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
        print(f"\t - Installing {self}")

        def install_local():
            print("\t\tLocal Package")
            print(f"\t\tInstalling into {APPDATA}")

        def install_git():
            print("\t\tGit Package")

        match self.type:
            case PackageTypes.LOCAL:
                install_local()
            case PackageTypes.GIT:
                install_git()

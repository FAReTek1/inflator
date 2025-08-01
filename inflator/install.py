from typing import Self, Optional
from dataclasses import dataclass
from enum import Enum, auto

from furl import furl

def install(pkgs: list[str]):
    print(f"INSTALL: {pkgs}")

    for pkg in pkgs:
        install_pkg(pkg)


def install_pkg(pkg: str):
    pkg: Package = Package.parse(pkg)
    print(f"\t - Installing {pkg}")


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

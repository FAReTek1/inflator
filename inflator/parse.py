# If we cannot locate a inflator.toml file, try to resolve stuff from goboscript.toml
# Note that these packages will need to be imported into backpack/ instead of inflate/
from __future__ import annotations

import logging

from dataclasses import dataclass
from typing import Optional

from inflator import package


@dataclass
class IFToml:
    username: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None

    deps: Optional[list[package.Package]] = None


def parse_gstoml(toml: dict):
    logging.info(f"Parsing gstoml {toml}")
    deps = []

    for name, src in toml.get("dependencies", {}).items():
        split = src.split("==")
        version = split[-1]
        url = '=='.join(split[:-1])

        if url == '':
            # we are probably dealing with an old goboscript package, using the '@' syntax
            split = src.split("@")
            version = split[-1]
            url = '@'.join(split[:-1])

        deps.append(package.Package.from_raw(url, version=version, importname=name))

    return IFToml(deps=deps)


def parse_iftoml(toml: dict):
    logging.info(f"Parsing iftoml {toml}")
    deps = []
    tdeps = toml.get("dependencies", {})

    for name, value in tdeps.items():
        if isinstance(value, str):
            raw, version = value, "*"
        else:
            assert isinstance(value, list)
            assert len(value) == 2

            raw, version = value

        deps.append(
            package.Package.from_raw(raw, version=version, importname=name)
        )

    return IFToml(
        username=toml.get("username"),
        name=toml.get("name"),
        version=toml.get("version"),
        deps=deps
    )

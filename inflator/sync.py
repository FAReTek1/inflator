import pprint
import tomllib
import os
from typing import Any

from inflator.install import search_for_package, Package, get_toml_data, install
from inflator import gstoml
from inflator.util import APPDATA_FARETEK_INFLATE


def locate_package(name, data: str | dict[str, Any]):
    raw = data.get()

    split = raw.split('/')

    if len(split) < 3:
        split += [None] * (3 - len(split))
    elif len(split) > 3:
        split = split[:3]

    split = [i if i else None for i in split]

    username, reponame, version = split
    return search_for_package(reponame, version, username, msg=False)


def sync(fp: str):
    print(f"- Synchronizing libraries in {fp!r}")
    data, deps, _ = get_toml_data(fp)

    # pprint.pp(data)
    # pprint.pp(deps)

    for name, data in deps.items():
        print(f"\t- Packaging {name!r}: {data=}")

        # locate that package!
        location = locate_package(name, data)[0]
        print(f"\t\tFound package: {location}")

        sync(f"{APPDATA_FARETEK_INFLATE}\\{location}")

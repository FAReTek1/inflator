import logging
import os
import re
import pprint
import io
import shutil
import tomllib

from typing import Self, Optional
from dataclasses import dataclass
from enum import Enum, auto
from zipfile import ZipFile

import httpx

from furl import furl

from inflator import gstoml
from inflator.util import APPDATA_FARETEK


def install(raw: str, version: str = None):
    pkg = Package.parse(raw)
    pkg.version = version
    pkg.install()


class PackageTypes(Enum):
    LOCAL = auto()
    GIT = auto()  # currently only actually supports GitHub. maybe refactor??


@dataclass
class Package:
    raw: str
    type: PackageTypes


    username: Optional[str] = None
    reponame: Optional[str] = None  # = name
    version: Optional[str] = None

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

    def _parse_gh_link(self):
        f = furl(self.raw)

        assert f.host
        segments = f.path.segments
        assert len(segments) == 2  # must be: username, reponame

        self.username, self.reponame = segments

        print(f"\tParsed url as {self.reponame!r} by {self.username!r}")

    def __str__(self):
        return self.raw

    def _fetch_newest_tag(self) -> str:
        print("\tFetching version name from gh...")
        tags = (httpx.get(f"https://api.github.com/repos/{self.username}/{self.reponame}/tags")
                .raise_for_status()
                .json())
        newest_tag = tags[0]
        return newest_tag["name"]

    @property
    def file_location(self):
        return f"{APPDATA_FARETEK}\\{self.reponame}\\{self.version}\\"

    def install(self):
        print(f"- Installing {self}")

        def install_local():
            print("\tLocal Package")
            print("\tFetching goboscript.toml/inflate.toml")
            print(f"\tInstalling into {APPDATA_FARETEK}")

            # need to read inflator.toml to fetch name and version
            print("\tReading inflator.toml for name/version")
            raw_toml = open(os.path.join(self.raw, "inflator.toml")).read()

            data = tomllib.loads(raw_toml)

            # These are required fields!
            self.reponame = data["name"]
            self.version = data["version"]
            print(f"\tLoaded {self.reponame!r} version={self.version!r}")
            print(f"\tInstalling into {self.file_location}")

            shutil.copytree(self.raw, self.file_location, dirs_exist_ok=True)

        def install_git():
            print("\tGit Package")
            self._parse_gh_link()

            if not self.version:
                self.version = self._fetch_newest_tag()

            def fetch_data():
                print(f"\tFetching version {self.version!r}")

                try:
                    resp = httpx.get(
                        f"https://api.github.com/repos/{self.username}/{self.reponame}/zipball/refs/tags/{self.version}",
                        follow_redirects=True).raise_for_status()
                except httpx.HTTPError as e:
                    e.add_note(f"Tag seems to be invalid. Maybe you meant {self._fetch_newest_tag()!r}?")
                    raise e

                return resp.content

            data = fetch_data()
            with ZipFile(io.BytesIO(data)) as archive:
                archive.extractall(self.file_location)

        match self.type:
            case PackageTypes.LOCAL:
                install_local()
            case PackageTypes.GIT:
                install_git()

        assert self.reponame
        assert self.version

        root, dirs, _ = next(os.walk(self.file_location))
        root_dir = root + dirs[0]

        toml_gs = None
        toml_if = None
        if os.path.exists(fp := f"{root_dir}\\goboscript.toml"):
            print(f"\tReading {fp}")
            toml_gs = open(fp).read()
        if os.path.exists(fp := f"{root_dir}\\inflator.toml"):
            print("\tReading {fp}")
            toml_if = open(fp).read()

        print(f"{toml_gs!r}\n{toml_if!r}")

import logging
import os
import re
import pprint
import io
import shutil
import tomllib
import fnmatch

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
        assert len(segments) == 2  # must be: username, reponame. **Remove any trailing slashes!**

        self.username, self.reponame = segments

        print(f"\tParsed url as {self.reponame!r} by {self.username!r}")

    def __str__(self):
        return self.raw

    def _fetch_newest_tag(self, pattern="*") -> str:
        print("\tFetching version name from gh...")
        tags = (httpx.get(f"https://api.github.com/repos/{self.username}/{self.reponame}/tags")
                .raise_for_status()
                .json())

        matched_tag = None
        for tag in tags:
            name = tag["name"]
            if fnmatch.fnmatch(name, pattern):
                matched_tag = tag
                break


        assert isinstance(matched_tag, dict)

        return matched_tag["name"]

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
            try:
                raw_toml = open(os.path.join(self.raw, "inflator.toml")).read()
            except FileNotFoundError as e:
                e.add_note(f"No inflator.toml file! This is required for local packages. "
                           f"Either make a inflator.toml file, or check your input directory")
                raise e

            data = tomllib.loads(raw_toml)

            # These are required fields!
            self.reponame = data["name"]
            self.version = data["version"]
            print(f"\tLoaded {self.reponame!r} version={self.version!r}")
            print(f"\tInstalling into {self.file_location}")

            if os.path.exists(self.file_location):
                shutil.rmtree(self.file_location)
            shutil.copytree(self.raw, os.path.join(self.file_location, self.reponame))

        def install_git():
            # it says git but it means github
            print("\tGit Package")
            self._parse_gh_link()

            if not self.version:
                self.version = self._fetch_newest_tag()
            else:
                self.version = self._fetch_newest_tag(self.version)

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

        data = {"dependencies": None}  # Prevent errors when trying to delete "dependencies" if it doesn't exist
        deps = {}
        if os.path.exists(fp := f"{root_dir}\\goboscript.toml"):
            print(f"\tReading {fp!r}")
            gs_data, gs_deps = gstoml.parse_gstoml(tomllib.load(open(fp, "rb")))
            data |= gs_data
            deps |= gs_deps

        if os.path.exists(fp := f"{root_dir}\\inflator.toml"):
            print(f"\tReading {fp!r}")
            if_data, if_deps = gstoml.parse_iftoml(tomllib.load(open(fp, "rb")))
            data |= if_data
            deps |= if_deps

        del data["dependencies"]  # only use deps

        print(f"\t{data=}")
        print(f"\t{deps=}")

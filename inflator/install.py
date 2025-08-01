import os
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
from inflator.util import APPDATA_FARETEK_PKGS


def install(raw: str, version: str = None, *, upgrade: bool = False, ids: list[str] = None):
    # ids is a list to keep track of packages that have been imported to prevent circular dependencies
    pkg = Package.parse(raw)
    pkg.version = version
    pkg.install(upgrade=upgrade, ids=ids)
    return pkg


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

    backpack_only: Optional[bool] = None

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

        if matched_tag is None:
            if tags:
                raise ValueError("Matching tag could not be found, but alternatives available. Consider choosing {!r}"
                                 .format(tags[-1]["name"]))
            else:
                raise ValueError("No tags to match against.")

        return matched_tag["name"]

    @property
    def file_location(self):
        return f"{APPDATA_FARETEK_PKGS}\\{self.username}\\{self.reponame}\\{self.version}\\"

    @property
    def id(self):
        return f"{self.username}\\{self.reponame}\\{self.version}"

    def install(self, *, upgrade: bool = False, ids: list[str] = None):
        if ids is None:
            ids = []

        if not upgrade:
            # search for package
            ...

        print(f"- Installing {self}")

        def install_local():
            print("\tLocal Package")
            print("\tFetching goboscript.toml/inflate.toml")
            print(f"\tInstalling into {APPDATA_FARETEK_PKGS}")

            # need to read inflator.toml to fetch name and version
            print("\tReading inflator.toml for name/version")
            try:
                raw_toml = open(os.path.join(self.raw, "inflator.toml")).read()
            except FileNotFoundError as e:
                e.add_note(f"No inflator.toml file! This is required for local packages. "
                           f"Either make a inflator.toml file, or check your input directory")
                raise e

            toml_data = tomllib.loads(raw_toml)

            # These are required fields!
            if self.username is None:
                self.username = toml_data.get("username", "LOCAL")
            self.reponame = toml_data["name"]  # please add a name=... value in inflator.toml
            self.version = toml_data["version"]  # please add a version=... value in inflator.toml
            print(f"\tLoaded {self.reponame!r} version={self.version!r}")
            print(f"\tInstalling into {self.file_location}")

            if os.path.exists(self.file_location):
                shutil.rmtree(self.file_location)
            shutil.copytree(self.raw, os.path.join(self.file_location, self.reponame))

        def install_git():
            # it says git but it means GitHub
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

            zip_data = fetch_data()
            with ZipFile(io.BytesIO(zip_data)) as archive:
                archive.extractall(self.file_location)

        match self.type:
            case PackageTypes.LOCAL:
                install_local()
            case PackageTypes.GIT:
                install_git()

        assert self.username
        assert self.reponame
        assert self.version

        assert self.id not in ids  # Make sure you do not have circular dependencies
        ids.append(self.id)

        root, dirs, _ = next(os.walk(self.file_location))
        root_dir = root + dirs[0]

        data, deps, self.backpack_only = get_toml_data(root_dir)

        print(f"\t{data=}")
        print(f"\t{deps=}")

        for _, attrs in deps.items():
            install(attrs["raw"], attrs["version"], ids=ids)


def search_for_package(reponames: Optional[list[str] | str] = None,
                       versions: Optional[list[str] | str] = None,
                       usernames: Optional[list[str] | str] = None,
                       *, msg: bool=True) -> list[str]:
    """
    Find all repos that fit the query
    :return: list[str] - list of string in format {username}\\{reponame}\\{version}
    """

    def handle_l(ls):
        # handle list so that it can work nicely. None -> [], single string -> [str]
        if isinstance(ls, str):
            ls = [ls]
        elif ls is None:
            ls = []

        return [i.lower() for i in ls]

    reponames = handle_l(reponames)
    versions = handle_l(versions)
    usernames = handle_l(usernames)

    if msg:
        print(f"Searching for {reponames!r} {versions} by {usernames!r}")
    _, local_usernames, _ = next(os.walk(APPDATA_FARETEK_PKGS))

    results: list[str] = []

    for username in filter(lambda u: not usernames or u.lower() in usernames, local_usernames):
        root, local_reponames, _ = next(os.walk(f"{APPDATA_FARETEK_PKGS}\\{username}"))

        for reponame in filter(lambda r: not reponames or r.lower() in reponames, local_reponames):
            _, local_versions, _ = next(os.walk(f"{root}\\{reponame}"))

            for version in filter(lambda v: not versions or v.lower() in versions, local_versions):
                results.append(f"{username}\\{reponame}\\{version}")

    return results


def get_toml_data(root_dir):
    data = {"dependencies": None}  # Prevent errors when trying to delete "dependencies" if it doesn't exist
    deps = {}
    backpack_only = None
    if os.path.exists(fp := f"{root_dir}\\goboscript.toml"):
        print(f"\tReading {fp}")
        gs_data, gs_deps = gstoml.parse_gstoml(tomllib.load(open(fp, "rb")))
        data |= gs_data
        deps |= gs_deps
        backpack_only = True

    if os.path.exists(fp := f"{root_dir}\\inflator.toml"):
        print(f"\tReading {fp}")
        if_data, if_deps = gstoml.parse_iftoml(tomllib.load(open(fp, "rb")))
        data |= if_data
        deps |= if_deps
        backpack_only = False

    del data["dependencies"]  # only use deps

    return data, deps, backpack_only

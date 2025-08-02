from __future__ import annotations

import fnmatch
import logging
import pathlib
import hashlib
import pprint
import shutil
import tomllib

from dataclasses import dataclass, field
from typing import Optional, Self, Any
from zipfile import ZipFile
from io import BytesIO

import httpx

from furl import furl

from inflator.util import APPDATA_FARETEK_PKGS, APPDATA_FARETEK_ZIPAREA
from inflator.parse import parse_iftoml, parse_gstoml


@dataclass
class Package:
    username: Optional[str]
    reponame: str
    version: str

    raw: Optional[str] = None
    local_path: Optional[pathlib.Path] = None
    importname: Optional[str] = None
    is_local: Optional[bool] = None
    backpack_only: Optional[bool] = None

    _resolved_version: Optional[str] = None
    deps: list[Package] = field(default_factory=list)

    @property
    def id(self):
        idstr = f"{self.username}\\{self.reponame}\\{self.version}"
        # hashing this to force use of this purely as an id, and not for string manipulation
        return hashlib.md5(idstr.encode()).hexdigest()

    @classmethod
    def from_raw(cls, raw: str, *, importname: Optional[str] = None, username: Optional[str] = None, reponame: Optional[str] = None, version: str = '*',
                 _id: Optional[str] = None) -> Self:
        f = furl(raw)

        if f.host:
            assert f.host == 'github.com'  # Online packages must be from gh. no other website allowed.

            segments = f.path.normalize().segments
            if segments[-1] == '':
                segments = segments[:-1]

            assert len(segments) == 2
            username, reponame = segments
            local_path = None
            is_local = False
        else:
            local_path = pathlib.Path(raw)

            username = None
            reponame = local_path.parts[-1]
            is_local = True
        self = cls(
            username=username,
            reponame=reponame,
            version=version,
            importname=importname,
            local_path=local_path,
            raw=raw,
            is_local=is_local,
        )

        if self.id == _id and _id is not None:
            raise ValueError(f"Circular import of {self}")
        if username is not None:
            self.username = username
        if reponame is not None:
            self.reponame = reponame

        if self.is_local:
            self.resolve_toml_info()

        return self

    @property
    def install_path(self):
        return APPDATA_FARETEK_PKGS / self.username / self.reponame / self.version

    @property
    def zip_path(self):
        return APPDATA_FARETEK_ZIPAREA / self.username / self.reponame / self.version

    def toml_path(self, name):
        return self.local_path / f"{name}.toml"

    def toml_file(self, name):
        return open(self.toml_path(name), "rb")

    def resolve_toml_info(self, _id: Optional[str] = None):
        assert self.local_path

        _id = self.id
        self.backpack_only = not self.toml_path("inflator").exists() and self.toml_path("goboscript").exists()

        if self.toml_path("inflator").exists():
            logging.info("Reading inflator.toml for name/version")

            data = parse_iftoml(tomllib.load(self.toml_file("inflator")), _id)

            if data.username:
                self.username = data.username
                logging.info(f"{self.username=}")

            if data.name:
                self.reponame = data.name
                logging.info(f"{self.reponame=}")

            if data.version:
                self.version = data.version
                logging.info(f"{self.version=}")

            self.deps += data.deps

        if self.toml_path("goboscript").exists():
            logging.info("Reading goboscript.toml for info")

            data = parse_gstoml(tomllib.load(self.toml_file("goboscript")), _id)

            logging.info(f"goboscript toml_data: {data}")

            self.deps += data.deps

        logging.info(f"Resolved {self.deps=}")

    def fetch_tag(self, pattern="*"):
        logging.info(f"Looking for tag for {self} with pattern {pattern}")
        assert not self.is_local

        logging.info(f"Fetching version name from github for {self}")

        tags: list[dict[str, Any]] = (httpx.get(f"https://api.github.com/repos/{self.username}/{self.reponame}/tags")
                                      .raise_for_status()
                                      .json())

        logging.info(f"Collected tags: {pprint.pformat(tags)}")

        for tag in tags:
            name = tag["name"]
            if fnmatch.fnmatch(name, pattern):
                logging.info(f"Matched tag: {name}")
                return name

        if not tags:
            raise ValueError("No tags to match against.")
        else:
            raise ValueError("Matching tag could not be found, but alternatives available. Consider choosing {!r}"
                             .format(tags[-1]["name"]))

    def fetch_data(self):
        logging.info(f"Trying to download {self} from gh")
        assert not self.is_local

        try:
            resp = httpx.get(
                f"https://api.github.com/repos/{self.username}/{self.reponame}/zipball/refs/tags/{self.version}",
                follow_redirects=True).raise_for_status()
        except httpx.HTTPError as e:
            e.add_note(f"Tag seems to be invalid. Maybe you meant {self.fetch_tag()!r}?")
            raise e

        logging.info(f"Downloaded {resp.content.__sizeof__()} bytes with status code {resp.status_code}")

        return resp.content

    def install(self, ids: Optional[list[str]] = None, update: bool = False):
        if ids is None:
            ids = [self.id]
        elif self.id in ids:
            # not that you are allowed to depend on an old version of yourself
            raise RecursionError(f"Circular import of {self}")

        if self.is_local:
            print(search_for_package(
                self.username, self.reponame, self.version
            ))

            logging.info(f"Installing local package {self}")
            logging.info(f"Installing into {self.install_path}")

            shutil.rmtree(self.install_path, ignore_errors=True)
            shutil.copytree(self.local_path, self.install_path)

        else:
            logging.info(f"Installing gh package {self}")

            if not self.version:
                self.version = "*"
            self.version = self.fetch_tag(self.version)

            zipball = self.fetch_data()

            shutil.rmtree(self.zip_path, ignore_errors=True)
            with ZipFile(BytesIO(zipball)) as archive:
                archive.extractall(self.zip_path)

            _, dirs, _ = next(self.zip_path.walk())
            extraction_path = self.zip_path / dirs[0]
            logging.info(f"Moving {extraction_path} to {self.install_path}")

            shutil.rmtree(self.install_path, ignore_errors=True)
            shutil.move(extraction_path, self.install_path)
            shutil.rmtree(self.zip_path, ignore_errors=True)

            self.local_path = self.install_path
            self.resolve_toml_info()

        print(f"Collected {self.deps}")
        for dep in self.deps:
            dep.install(ids)

        print(f"Installed {self.reponame} {self.version} by {self.username} into {self.install_path}")


def search_for_package(usernames: Optional[list[str] | str] = None,
                       reponames: Optional[list[str] | str] = None,
                       versions: Optional[list[str] | str] = None):
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

    logging.info(f"Searching for {reponames!r} {versions} by {usernames!r}")
    _, local_usernames, _ = next(APPDATA_FARETEK_PKGS.walk())

    results = []

    for username in filter(lambda u: not usernames or u.lower() in usernames, local_usernames):
        path1 = APPDATA_FARETEK_PKGS / username
        _, local_reponames, _ = next(path1.walk())

        for reponame in filter(lambda r: not reponames or r.lower() in reponames, local_reponames):
            path2 = path1 / reponame
            _, local_versions, _ = next(path2.walk())

            for version in filter(lambda v: not versions or v.lower() in versions, local_versions):
                install_path = path2 / version
                results.append(Package.from_raw(install_path, username=username, reponame=reponame, version=version))
    return results

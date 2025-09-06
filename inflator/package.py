from __future__ import annotations

import fnmatch
import logging
import os
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

from inflator.util import APPDATA_FARETEK_PKGS, APPDATA_FARETEK_ZIPAREA, rmtree
from inflator.parse import parse_iftoml, parse_gstoml
from inflator.cookies import gh
from inflator import gtp


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

    deps: list[Package] = field(default_factory=list)

    @property
    def id(self):
        idstr = f"{self.username}\\{self.reponame}\\{self.version}"
        # hashing this to force use of this purely as an id, and not for string manipulation
        return hashlib.md5(idstr.encode()).hexdigest()

    @classmethod
    def from_raw(cls, raw: str, *, importname: Optional[str] = None, username: Optional[str] = None,
                 reponame: Optional[str] = None, version: str = '*',
                 _id: Optional[str] = None) -> Self:
        f = furl(raw)

        if f.host:
            assert f.host == 'github.com'  # Online packages must be from gh. no other website allowed.

            segments = f.path.normalize().segments
            if segments[-1] == '':
                segments = segments[:-1]

            assert len(segments) == 2
            _username, _reponame = segments
            local_path = None
            is_local = False
        else:
            local_path = pathlib.Path(raw).resolve()
            if local_path.exists():
                _username = None
                _reponame = local_path.parts[-1]
                is_local = True
            else:
                # try and fetch from the gtp
                print("Loading from gtp: ")
                data = gtp.load()
                if raw in data:
                    return cls.from_raw(data[raw]["url"], importname=importname, username=username, reponame=reponame, version=version, _id=_id)
                else:
                    raise FileNotFoundError(f"File {raw} not found")

        self = cls(
            username=_username,
            reponame=_reponame,
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
    def name(self):
        return f"{self.reponame} {self.version} by {self.username}"

    @property
    def install_path(self):
        return APPDATA_FARETEK_PKGS / str(self.username) / self.reponame / self.version

    @property
    def zip_path(self):
        assert self.username is not None  # You can't have a GitHub package without a username
        return APPDATA_FARETEK_ZIPAREA / self.username / self.reponame / self.version

    def toml_path(self, name):
        return self.local_path / f"{name}.toml"

    def toml_file(self, name):
        return open(self.toml_path(name), "rb")

    def resolve_toml_info(self, _id: Optional[str] = None):
        assert self.local_path

        _id = self.id
        self.backpack_only = (not self.toml_path("inflator").exists()) and self.toml_path("goboscript").exists()

        logging.info("For self={}, iftoml_exists={}, gstoml_exists={}"
                     .format(self,
                             self.toml_path("inflator").exists(),
                             self.toml_path("goboscript").exists()))
        logging.info(f"So {self.backpack_only=}")

        if self.toml_path("inflator").exists():
            logging.info("Reading inflator.toml for name/version")

            data = parse_iftoml(tomllib.load(self.toml_file("inflator")), _id)

            # prioritise existing data over toml data. e.g. a package may be by inflated-goboscript but registered
            # as by faretek1
            if data.username and not self.username:
                self.username = data.username
                logging.info(f"{self.username=}")

            if data.name and not self.name:
                self.reponame = data.name
                logging.info(f"{self.reponame=}")

            if data.version and not self.version:
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

        tags = gh.get_repo(f"{self.username}/{self.reponame}").get_tags()

        logging.info(f"Collected tags: {pprint.pformat(tags)}")

        for tag in tags:
            name = tag.name
            if fnmatch.fnmatch(name, pattern):
                logging.info(f"Matched tag: {name}")
                return name

        if not tags:
            raise ValueError("No tags to match against.")
        else:
            raise ValueError("Matching tag could not be found, but alternatives available. Consider choosing {!r}"
                             .format(tags[-1].name))

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

    @property
    def already_installed(self):
        pks = search_for_package(self.username, self.reponame, self.version)

        if pks:
            print("Found {} existing installation(s): {}"
                  .format(len(pks),
                          ''.join(f"\n- {pk.name}" for pk in pks)))
            return True

        return False

    def install(self, ids: Optional[list[str]] = None, editable: bool = False, upgrade: bool = False):
        if ids is None:
            ids = [self.id]
        elif self.id in ids:
            # not that you are allowed to depend on an old version of yourself
            raise RecursionError(f"Circular import of {self}")

        if self.is_local:
            if not upgrade:
                if self.already_installed:
                    return

            logging.info(f"Installing local package {self}")
            logging.info(f"Installing into {self.install_path}")

            if self.install_path.is_symlink():
                self.install_path.unlink()
            else:
                rmtree(self.install_path, ignore_errors=True)

            if editable:
                os.makedirs(pathlib.Path(*self.install_path.parts[:-1]), exist_ok=True)
                self.install_path.symlink_to(self.local_path)
            else:
                shutil.copytree(self.local_path, self.install_path, symlinks=True)

        else:
            logging.info(f"Installing gh package {self}")

            if not self.version:
                self.version = "*"
            self.version = self.fetch_tag(self.version)

            if not upgrade:
                if self.already_installed:
                    return

            zipball = self.fetch_data()

            shutil.rmtree(self.zip_path, ignore_errors=True)
            with ZipFile(BytesIO(zipball)) as archive:
                archive.extractall(self.zip_path)

            _, dirs, _ = next(self.zip_path.walk())
            extraction_path = self.zip_path / dirs[0]
            logging.info(f"Moving {extraction_path} to {self.install_path}")

            if self.install_path.is_symlink():
                self.install_path.unlink()
            else:
                rmtree(self.install_path, ignore_errors=True)
            shutil.move(extraction_path, self.install_path)
            rmtree(self.zip_path, ignore_errors=True)

            self.local_path = self.install_path
            self.resolve_toml_info()

        print(f"Collected {self.deps}")
        for dep in self.deps:
            # Don't pass in editable.
            dep.install(ids, upgrade=upgrade)

        print(f"Installed {self.name} into {self.install_path}")

    def resolve(self) -> Self:
        pkgs = search_for_package(self.username, self.reponame, self.version)
        if len(pkgs) > 1:
            logging.info(f"Multiple packages resolved for {self}\n\t{pkgs}")
        elif len(pkgs) == 0:
            logging.warning(f"Could not resolve {self}")
            return self

        pkg = pkgs[0]
        self.username = pkg.username
        self.reponame = pkg.reponame
        self.version = pkg.version
        self.backpack_only = pkg.backpack_only

        if not self.local_path:
            self.local_path = pkg.local_path

        logging.info(f"Resolved {self=}")
        self.resolve_toml_info()

        return self

    @property
    def symlink_folder(self):
        return "backpack" if self.backpack_only else "inflator"


def search_for_package(usernames: Optional[list[str] | str] = None,
                       reponames: Optional[list[str] | str] = None,
                       versions: Optional[list[str] | str] = None,
                       globbed: bool = True):
    """
    Find all repos that fit the query. Uses globs unless specified otherwise
    :return: list[str] - list of string in format {username}\\{reponame}\\{version}
    """

    def handle_l(ls):
        # handle list so that it can work nicely. None -> [], single string -> [str]
        if isinstance(ls, str):
            ls = [ls]
        elif ls is None:
            ls = []

        return ls

    reponames = [r.lower() for r in handle_l(reponames)]
    versions = handle_l(versions)
    usernames = [u.lower() for u in handle_l(usernames)]

    logging.info(f"Searching for {reponames!r} {versions} by {usernames!r}")
    try:
        _, local_usernames, _ = next(APPDATA_FARETEK_PKGS.walk())

        results = []

        def match_l(pats, value):
            if globbed:
                return not pats or any(fnmatch.fnmatch(value, p) for p in pats)
            else:
                return not pats or value in pats

        for username in filter(lambda i: match_l(usernames, i.lower()), local_usernames):
            logging.info(f"\tSearching for {username=}")
            path1 = APPDATA_FARETEK_PKGS / username
            _, local_reponames, _ = next(path1.walk())

            for reponame in filter(lambda i: match_l(reponames, i.lower()), local_reponames):
                logging.info(f"\tSearching for {reponame=}")

                path2 = path1 / reponame
                _, local_versions, possible_symlinks = next(path2.walk())

                local_versions += [s for s in possible_symlinks if (path2 / s).is_symlink()]

                # Make newer versions come first.
                # Because v1.0.0 is before v0.0.0 in alphabetical order, we can just do a reverse string list sort
                local_versions.sort(reverse=True)

                for version in filter(lambda i: match_l(versions, i.lower()), local_versions):
                    logging.info(f"\tSearching for {version=}")

                    install_path = path2 / version
                    pkg = Package.from_raw(install_path, username=username, reponame=reponame, version=version)
                    results.append(pkg)

                    logging.info(f"\tGot {pkg}")
        return results
    except StopIteration as e:
        logging.info(f"Caught exception {e}")
        logging.info("Making appdata dirs because they don't seem to exist")

        os.makedirs(APPDATA_FARETEK_PKGS)
        return []

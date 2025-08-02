from __future__ import annotations

import fnmatch
import logging
import pathlib
import hashlib
import pprint
import tomllib

from dataclasses import dataclass, field
from typing import Optional, Self, Any

import httpx

from furl import furl

from inflator.util import APPDATA_FARETEK_PKGS
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

    _resolved_version: Optional[str] = None
    deps: list[Package] = field(default_factory=list)

    @property
    def id(self):
        idstr = f"{self.username}\\{self.reponame}\\{self.version}"
        # hashing this to force use of this purely as an id, and not for string manipulation
        return hashlib.md5(idstr.encode()).hexdigest()

    @classmethod
    def from_raw(cls, raw: str, *, importname: Optional[str] = None, version: str = '*') -> Self:
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

        if self.is_local:
            self.resolve_toml_info()

        return self

    def toml_path(self, name):
        return self.local_path / f"{name}.toml"

    def toml_file(self, name):
        return open(self.toml_path(name), "rb")

    def resolve_toml_info(self):
        assert self.local_path

        if self.toml_path("inflator").exists():
            logging.info("Reading inflator.toml for name/version")

            data = parse_iftoml(tomllib.load(self.toml_file("inflator")))

            if data.username:
                self.username = data.username
                logging.info(f"{self.username=}")

            if data.name:
                self.reponame = data.name
                logging.info(f"{self.reponame=}")

        if self.toml_path("goboscript").exists():
            logging.info("Reading goboscript.toml for info")

            data = parse_iftoml(tomllib.load(self.toml_file("goboscript")))

            logging.info(f"goboscript toml_data: {data}")

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

        return resp.content

    def install(self, ids: Optional[list[str]] = None):
        print(self)
        if ids is None:
            ids = [self.id]

        if self.is_local:
            logging.info(f"Installing local package {self}")
            logging.info(f"Installing into {APPDATA_FARETEK_PKGS}")
        else:
            logging.info(f"Installing gh package {self}")

            if not self.version:
                self.version = "*"
            self.version = self.fetch_tag(self.version)


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

    raise NotImplementedError

from __future__ import annotations

import logging

from inflator.util import APPDATA_FARETEK_PKGS
from inflator.package import Package


def install(raw: str, version: str = "*", *, upgrade: bool = False, ids: list[str] = None, editable: bool = False):
    logging.info(f"Raw install: {raw}")

    if ids is None:
        ids = []

    pkg = Package.from_raw(raw, version=version)
    logging.info(f"Parsed as {pkg}")
    pkg.install(ids=ids, editable=editable, upgrade=upgrade)

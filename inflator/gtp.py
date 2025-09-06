from __future__ import annotations

import json

from base64 import b64decode

from inflator.cookies import gh

_repo = None
def repo():
    global _repo

    if not _repo:
        _repo = gh.get_repo("inflated-goboscript/gtp")

    return _repo

def load() -> dict[str, dict[str, str]]:
    raw_data = repo().get_contents("gtp.json")
    assert raw_data is not None, "No data. Something went wrong with GitHub api. raise issue on gh"
    return json.loads(b64decode(raw_data.content).decode())

from __future__ import annotations

import json

from typing import Optional
from base64 import b64decode

import httpx


def load() -> dict[str, dict[str, str]]:
    raw_data: Optional[str] = (httpx.get("https://api.github.com/repos/inflated-goboscript/gtp/contents/gtp.json")
                               .raise_for_status()
                               .json()
                               .get("content"))

    assert raw_data is not None, "No data. Something went wrong with GitHub api. raise issue on gh"
    data = b64decode(raw_data).decode()
    return json.loads(data)

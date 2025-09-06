# store 'cookies' in appdata
import json

from typing import Any

from inflator.util import APPDATA_FARETEK_COOKIES


class _Cookies:
    def __init__(self):
        (APPDATA_FARETEK_COOKIES / '..').resolve().mkdir(parents=True, exist_ok=True)
        if not APPDATA_FARETEK_COOKIES.exists():
            APPDATA_FARETEK_COOKIES.write_text("{}")

    @property
    def data(self):
        return json.load(APPDATA_FARETEK_COOKIES.open())

    @data.setter
    def data(self, data: dict[str, str | int | None | bool | float | list | dict[str, Any]]):
        json.dump(data, APPDATA_FARETEK_COOKIES.open("w"))

    def __setitem__(self, key: str, value: str | int | None | bool | float | list | dict[str, Any]):
        self.data |= {key: value}

    def __getitem__(self, key):
        return self.data[key]


cookies = _Cookies()

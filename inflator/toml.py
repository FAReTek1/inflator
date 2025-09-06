from pathlib import Path

from inflator.util import ERROR_MSG, AURA


def toml(cwd: Path = None):
    if cwd is None:
        cwd = Path.cwd()

    fp = cwd / "inflator.toml"
    if fp.exists():
        print("Inflator.toml already exists!")
        return

    print(f"Creating {fp}")
    fp.write_text(f"""\
# inflator.toml syntax documentation: https://github.com/faretek1/inflator#inflator
name = {fp.parts[-2]!r}
version = \"v0.0.0\"
username = \"if this is left blank then {AURA}\"

[dependencies]
""")

import shutil
import subprocess

from pathlib import Path
from typing import Optional

from slugify import slugify


def new(name: Optional[str] = None):
    if name is None:
        name = Path.cwd().name
        output_dir = Path.cwd()
    else:
        name = slugify(name)
        output_dir = Path(name)

    output_dir = output_dir.resolve()
    goboscript_output_dir = (output_dir / "..").resolve()

    print(f"Making {name!r}, dir={output_dir}")

    assert shutil.which("goboscript"), "You need to install goboscript: https://github.com/aspizu/goboscript/"
    subprocess.run(["goboscript", "new", "-n", f"{name}"], cwd=str(goboscript_output_dir))


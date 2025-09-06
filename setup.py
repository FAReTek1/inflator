from pathlib import Path

import setuptools
from inflator import __version__

fdir = (Path(__file__) / '..').resolve()

setuptools.setup(
    name="inflate",
    version=__version__,
    packages=setuptools.find_packages(),

    entry_points={
        "console_scripts": [
            "inflate=inflator.__main__:main"
        ]
    },

    author="faretek1",
    description="Inflates gobos. A goboscript package manager.",
    long_description_content_type="text/markdown",
    long_description=(fdir / "readme.md").read_text(),
    install_requires=(fdir / "requirements.txt").read_text(),
    keywords=["goboscript"],
    project_urls={
        "Source": "https://github.com/inflated-goboscript/inflator",
    }
)

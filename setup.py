import setuptools
from inflator import __version__

setuptools.setup(
    name="inflator",
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
    long_description=open("README.md").read(),
    install_requires=open("requirements.txt").read(),
    keywords=["goboscript"],
    project_urls={
        "Source": "https://github.com/inflated-goboscript/inflator",
        "Documentation": "https://inflated-goboscript.github.io/inflator/",
        "Homepage": "https://inflated-goboscript.github.io/inflator/"
    }
)

import setuptools
from inflator import __version__

setuptools.setup(
    name='inflate',
    version=__version__,
    packages=setuptools.find_packages(),

    entry_points={
        'console_scripts': [
            'inflate=inflator.__main__:main'
        ]
    },

    author="faretek1",
    description="temp",
    long_description_content_type="text/markdown",
    long_description=open("readme.md").read(),
    install_requires=open("requirements.txt").read(),
    keywords=['goboscript'],
    project_urls={
        "Source": "https://github.com/faretek1/inflate",
    }
)

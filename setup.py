import setuptools

setuptools.setup(
    name='inflate',
    version='0.0.0',
    packages=setuptools.find_packages(),

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

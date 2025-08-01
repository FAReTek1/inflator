# If we cannot locate a inflator.toml file, try to resolve stuff from goboscript.toml
# Note that these packages will need to be imported into backpack/ instead of inflate/



toml_return = tuple[dict, dict[str, dict[str, str]]]


def parse_gstoml(toml: dict) -> toml_return:
    # print(f"\t{toml=}")
    deps = {}

    for name, src in toml.get("dependencies", {}).items():
        split = src.split("==")
        version = split[-1]
        url = '=='.join(split[:-1])

        if url == '':
            # we are probably dealing with an old goboscript package, using the '@' syntax
            split = src.split("@")
            version = split[-1]
            url = '@'.join(split[:-1])

        deps[name] = {"raw": url, "version": version}

    return {}, deps


def parse_iftoml(toml: dict) -> toml_return:
    # print(f"\t{toml=}")
    deps = {}
    tdeps = toml.get("dependencies", {})
    if isinstance(tdeps, list):
        for name in tdeps:
            deps[name] = None
    else:
        for name, value in tdeps.items():
            if isinstance(value, str):
                value = {"raw": value, "version": "*"}
            deps[name] = value

    return toml, deps
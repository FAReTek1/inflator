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

        deps[name] = {"raw": url, "version": version}

    return {}, deps


def parse_iftoml(toml: dict) -> toml_return:
    # print(f"\t{toml=}")
    deps = {}
    for name, value in toml.get("dependencies", {}).items():
        if isinstance(value, str):
            value = {"raw": value, "version": "*"}
        deps[name] = value

    return toml, deps

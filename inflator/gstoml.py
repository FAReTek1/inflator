# If we cannot locate a inflator.toml file, try to resolve stuff from goboscript.toml
# Note that these packages will need to be imported into backpack/ instead of inflate/

def parse_gstoml(toml: dict) -> tuple[dict, dict]:
    # print(f"\t{toml=}")
    deps = {}

    for name, src in toml.get("dependencies", {}).items():
        split = src.split("==")
        version = split[-1]
        url = '=='.join(split[:-1])

        deps[name] = {"url": url, "version": version}

    return {}, deps


def parse_iftoml(toml: dict) -> tuple[dict, dict]:
    # print(f"\t{toml=}")
    # probably no parsing necessary here
    return toml, toml["dependencies"]

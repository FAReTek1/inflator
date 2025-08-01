import os

from inflator.install import search_for_package, Package, get_toml_data, install
from inflator.util import APPDATA_FARETEK_PKGS


def sync(fp: str, *, _toplevel=True):
    print("Collecting packages...")

    def collect(_fp: str, *, _toplevel=False):
        print(f"\t- Synchronizing libraries in {_fp!r}")

        data, deps, _ = get_toml_data(_fp, msg=False)

        # pprint.pp(data)
        # pprint.pp(deps)

        ret = []
        for name, data in deps.items():
            print(f"\t\t- Packaging {name!r}")

            # locate that package!
            if "path" in data:
                path: str = data["path"]
                path: list[str] = path.split('/')
                args = [i if i else None for i in path]
                location = search_for_package(*args, msg=False)

                if not location:
                    raise ValueError(f"Could not find package {args}")
            else:
                location = search_for_package(reponames=name, msg=False)
                if not location:
                    raise ValueError(f"Could not find package {name!r}")

            location = location[0]

            pk_fp = os.path.join(APPDATA_FARETEK_PKGS, location)
            print(f"\t\t\tFound package: {location}")
            ret.append((name, pk_fp))

            _, dirs, _ = next(os.walk(pk_fp))
            pk_fp = os.path.join(pk_fp, dirs[0])

            ret += collect(pk_fp)
        return ret

    collection = collect(fp, _toplevel=True)

    print("Collected pkgs: \n- {}"
          .format('\n- '.join(map(lambda i: i[1], collection))))

    for name, pk_dir in collection:
        if os.path.exists(os.path.join(fp, "inflator.toml")):
            target = os.path.join(fp, "inflation")
        else:
            target = os.path.join(fp, "backpack")
        target = os.path.join(target, name)

        print(f"\t- Creating symlink for {pk_dir!r} into {target!r}")
        # os.symlink(path, target, True)

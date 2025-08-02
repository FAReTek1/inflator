from __future__ import annotations

import logging
import pathlib
import shutil
import os

from inflator import package


def sync(path: pathlib.Path):
    logging.info(f"Collecting packages in {path}")
    pkg = package.Package.from_raw(str(path))

    def collect(_pkg: package.Package, *, toplevel=False):
        # Don't include the original directory, because that isn't a package - just something using them
        ret = [] if toplevel else [_pkg]
        for dep in _pkg.deps:
            dep.resolve()
            ret += collect(dep)

        return ret

    deps = collect(pkg, toplevel=True)

    print("Collected:{}"
          .format(''.join(f"\n- {dep.name}" for dep in deps) if deps else " nothing"))

    if not deps:
        print("Nothing to sync, so nothing to do")
        return

    (path / "backpack").mkdir(exist_ok=True)
    (path / "inflator").mkdir(exist_ok=True)

    shutil.rmtree(path / "backpack", ignore_errors=True)
    shutil.rmtree(path / "inflator", ignore_errors=True)

    for dep in deps:
        sympath = path / dep.symlink_folder / dep.importname

        logging.info(f"Symlinking {sympath} into {dep.install_path}")

        assert dep.install_path.exists()  # You haven't installed the dependency, or you may have spelt something wrong.

        os.makedirs(pathlib.Path(*sympath.parts[:-1]), exist_ok=True)
        sympath.unlink(missing_ok=True)
        sympath.symlink_to(dep.install_path, target_is_directory=True)

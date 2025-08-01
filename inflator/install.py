def install(pkgs: list[str]):
    print(f"INSTALL: {pkgs}")

    for pkg in pkgs:
        install_pkg(pkg)


def install_pkg(pkg: str):
    print(f"installing {pkg!r}")

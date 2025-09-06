# inflator

> Inflate gobos.

### Inflator is a package manager for goboscript

## Installation

1. Clone the repository
2. Run `cd inflator`
3. Run `pip install .`

## Usage

Inflator will try to behave like the old [backpack](https://github.com/aspizu/backpack) version when dealing
with `goboscript.toml`.
In the future, it will probably not support the current backpack version/syntax.

If you want to integrate your project with inflator, add an `inflator.toml` file to your project.
This is the file that inflator will look at for config and dependencies.

### Installing packages/gobos

Inflator uses a loosely [pip](https://github.com/pypa/pip) inspired syntax.

The command for installing packages is  `inflate install`

- For installing a local package:
    - Ensure an `inflator.toml` file is provided (see below)
    - cd to inside your package, to the same level as `inflator.toml`
    - run `inflate install .`

> [!NOTE]
> You can find public gobos at https://github.com/topics/inflated-goboscript

- For installing GitHub packages
    - run `inflate install <link to github repository>`
    - Optionally supply a version (tag name):<br>
      `inflate install <link to github repository> -V <version>`

- For local package development
    - You can install an 'editable' package using the `-e` flag.
    - `inflate install -e .`
    - This will store a symlink in your appdata instead of copying the folder, which means that changes to the original
      package will take effect instantly. This is like how `pip installe -e .` behaves

Inflator will avoid installing packages which have already been installed (same username, reponame and version).
To override this, use the `-U` flag.

> [!NOTE]
> If you are a package developer using inflator, you can upload your gobos to GitHub.
> Remember to provide `inflator.toml`.
> Please also add the `inflated-goboscript` tag to your repository 

### Syncing packages/gobos

<details><summary>
Inflator.toml syntax:
</summary>

```toml
# These 3 are used for local installating of a package.
# They are only needed if you are making your own package.
# `username` is only needed to keep locally installed packages linked to a specific user.
# But it is recommended to always include your username here
name = "<name of your package, e.g. 'projectenv'>"
version = "<version string, e.g. v0.0.0>"
username = "<Your username, e.g. FAReTek1>"

[dependencies]
# This is used by any project that has dependencies
# Use a package by relative path
vec2 = "../vec2"

# use an existing installed package
# WARNING: This will NOT work with inflate install!
# This assumes that you have already INSTALLED a package named `quat`
# e.g. from GitHub, or locally
quat = "quat"

# Use a GitHub repository
geo2d = "https://github.com/FAReTek1/geo2d"

# Use a GitHub repository with a version.
# Version numbers also work with globbing
geo2d_v7 = ["https://github.com/FAReTek1/geo2d", "v*.*.7"]

# Use an INSTALLED package with a version
# These version nums can also be globbed
penv-inf = ["projectenv-inflated", "v0.0.2"]

# Use an INSTALLED package with a version and specify a username
penv-inf = ["projectenv-inflated", "v0.0.2", "faretek1"]
```

If you are creating a package, do not include dependencies which rely on something already being installed
(because inflator will try to evaluate them when trying to install your package, and will not be able to find their
source)

</details>

To sync packages:
> [!NOTE]
> If you are on windows, you will need permissions to create symlinks

1. cd to your goboscript project
2. run `inflate`
3. if you want to do this without cding, do `inflate -i <dir>`
4. pkgs will end up in `inflate/` or `backpack/` as symlinks

### Other commands
#### inflate find
This lists out all packages that fit the specified name, username, or version

Syntax:
`inflate find [reponame] -U [username] -V [version]`

Globbing is allowed
You can omit all fields to list out all installed gobos.

#### inflate parse
This prints out what inflator makes of a `goboscript.toml` or `inflator.toml` file.
Used for development, but you can use it too.

Syntax:
`inflate parse [filepath]`

#### inflate toml
This auto generates an `inflator.toml` file for you.
Recommended to run with `goboscript new <args>`
Make sure you set your username or else

#### inflate -V
Prints out the inflate version

#### inflate -L
Prints out the path to the log folder

### development installation

1. clone the GitHub repository
2. cd to the repo directory
3. do `pip install -e .`
4. you can use inflate using `inflate <args>`

## credits

banner image is partially from https://scratch.mit.edu/projects/317901726/remixtree/

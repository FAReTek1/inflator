# inflator

this is an alternative to backpack

work in progress

### usage

- to sync packages
  1. go to your goboscript project (cd)
  2. run `inflate`
  3. if you want to do this without cding, do `inflate -i <dir>`
  4. pkgs will end up in `inflate/`
- to install packages
  - pip inspired syntax.
  - `inflate install --gh <github link>@<version, if specified, resolves>`
  - `inflate install -e .`
  - `inflate install .`
  
### development installation
1. clone the github repository
2. cd to the repo directory
3. do `pip install -e .`
4. you can use inflate using `inflate <args>`

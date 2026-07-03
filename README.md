# sdbtool

A tool for converting Microsoft Application Compatibility Database (SDB) files to XML format.

--------

[![PyPI - Version](https://img.shields.io/pypi/v/sdbtool)](https://pypi.org/project/sdbtool/)
[![PyPI - License](https://img.shields.io/pypi/l/sdbtool)](https://pypi.org/project/sdbtool/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sdbtool)](https://pypi.org/project/sdbtool/)\
[![CI](https://github.com/learn-more/sdbtool/actions/workflows/python-test.yml/badge.svg?event=push)](https://github.com/learn-more/sdbtool/actions/workflows/python-test.yml)
[![Publish Python Package](https://github.com/learn-more/sdbtool/actions/workflows/python-publish.yml/badge.svg)](https://github.com/learn-more/sdbtool/actions/workflows/python-publish.yml)
[![codecov](https://codecov.io/gh/learn-more/sdbtool/graph/badge.svg?token=Z476TDD3B2)](https://codecov.io/gh/learn-more/sdbtool)



## Table of Contents

1. [Features](#features)
1. [Getting Started](#getting-started)
1. [Contributing](#contributing)

## Features<a id="features"></a>

- Parses SDB files used by Windows for application compatibility.
- Converts SDB data into readable XML or JSON format.
- Dump file attributes in SDB-recognizable format
- Useful for analysis, migration, or documentation.
- Pure Python and cross-platform - no native `apphelp.dll` dependency.


## Getting Started<a id="getting-started"></a>

### Installation

Sdbtool is available as [`sdbtool`](https://pypi.org/project/sdbtool/) on PyPI.

Invoke sdbtool directly with [`uvx`](https://docs.astral.sh/uv/):

```shell
uvx sdbtool sdb2xml your.sdb                        # Convert the file 'your.sdb' to xml, and print it to the console
uvx sdbtool sdb2xml your.sdb --output your.xml      # Convert the file 'your.sdb' to xml, and write it to 'your.xml'
uvx sdbtool sdb2json your.sdb                       # Convert the file 'your.sdb' to json, and print it to the console
uvx sdbtool sdb2json your.sdb --output your.json    # Convert the file 'your.sdb' to json, and write it to 'your.json'
uvx sdbtool sdb2xml old.sdb --target-os 0501        # Resolve tag names as of Windows XP (for older databases)
uvx sdbtool attributes your.exe                     # Show the file attributes as recognized by apphelp in an XML-friendly format
uvx sdbtool info your.sdb                           # Show some details about the SDB file (version, description, ...)
```

Or install sdbtool with `uv` (recommended), `pip`, or `pipx`:

```shell
# With uv.
uv tool install sdbtool@latest  # Install sdbtool globally.

# With pip.
pip install sdbtool

# With pipx.
pipx install sdbtool
```

Updating an installed sdbtool to the latest version with `uv`:
```shell
# With uv.
uv tool upgrade sdbtool

# With pip.
pip install --upgrade sdbtool

# With pipx.
pipx upgrade sdbtool
```

### Tag names and `--target-os`

Tag names are not constant across Windows versions: some are renamed (e.g. `OS_PLATFORM` became `GUEST_TARGET_PLATFORM`), and some are dropped (e.g. `OS_SKU` exists on XP but not on Windows 11).
`sdb2xml` / `sdb2json` therefore accept `--target-os <VERSION>` to resolve names as of a particular Windows release; without it, names are resolved against the newest known table.
An unknown tag is rendered as `InvalidTag_0xXXXX`.

### RUNTIME_PLATFORM (0x4021)

The tag id `0x4021` has two unrelated encodings depending on the database version:

- **Version 3** (Windows 10+): one DB-level tag holding a `(guest, host)` architecture **pair bitmask** (`RuntimePlatformType`, e.g. `AMD64 | X86_ON_AMD64`).
- **Version 2** (Vista..Windows 8.1): a **per-entry** tag holding a little-endian list of up to three host-platform selector bytes (`0x40 | code`), OR-combined, with bit `0x80000000` negating the match (`RuntimePlatformV2Type`). Codes: `0`=X86, `9`=AMD64, `6`=IA64, `12`=WOW64 (any 32-bit-on-64-bit), `13`=NATIVE64 (any native 64-bit). Reversed from `SdbpCheckRuntimePlatform` in pre-Win10 `apphelp.dll`; e.g. `0x4D4C40` -> `X86 | WOW64 | NATIVE64`.

sdbtool decodes each form according to the file's header major version.


## Contributing<a id="contributing"></a>

Contributions are welcome! Please open issues or submit pull requests.

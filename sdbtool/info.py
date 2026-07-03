"""
PROJECT:     sdbtool
LICENSE:     MIT (https://spdx.org/licenses/MIT)
PURPOSE:     Read high-level information about an SDB file.
COPYRIGHT:   Copyright 2025,2026 Mark Jansen <mark.jansen@reactos.org>
"""

import os
from dataclasses import dataclass
from uuid import UUID
from sdbtool.apphelp import sdb_reader

DB_INFO_FLAGS_VALID_GUID = 1
# Always set by the (Win10+) SdbGetDatabaseInformationByName implementation.
_DB_INFO_FLAGS_BASE = 0x10000000

_TAG_DATABASE = 0x7001
_TAG_RUNTIME_PLATFORM = 0x4021
_TAG_GUEST_TARGET_PLATFORM = 0x4023

# Maps a GUEST_TARGET_PLATFORM bit to the RUNTIME_PLATFORM (guest-on-host) bit an amd64
# host reports for it: x86 guest -> X86_ON_AMD64 (0x4), amd64 guest -> AMD64 (0x2).
# IA64/ARM/ARM64 guests are unsupported.
_GUEST_TO_AMD64_HOST = {0x1: 0x4, 0x4: 0x2}


@dataclass
class DatabaseInformation:
    """Database information structure."""

    Description: str | None
    dwMajor: int
    dwMinor: int
    dwFlags: int
    Id: UUID | None
    dwRuntimePlatform: int | None


def _runtime_platform(pdb: sdb_reader.SdbFile) -> int:
    """Reproduce the dwRuntimePlatform value reported by apphelp.dll on an amd64 host.

    A version-3 database with a RUNTIME_PLATFORM tag reports that tag's value unmodified.
    Otherwise (version-2 database, or tag absent) GUEST_TARGET_PLATFORM is read, defaulting to 0x1 (x86 guest), and each guest bit is mapped to the host's pair bit, e.g. guest 0x1 -> 4 (X86_ON_AMD64) and guest 0x4 -> 2 (AMD64).
    """
    root = sdb_reader.SdbFindFirstTag(pdb, sdb_reader.TAGID_ROOT, _TAG_DATABASE)
    if root == sdb_reader.TAGID_NULL:
        guest = 0x1
    else:
        if pdb.major != 2:
            tag = sdb_reader.SdbFindFirstTag(pdb, root, _TAG_RUNTIME_PLATFORM)
            if tag != sdb_reader.TAGID_NULL:
                return sdb_reader.SdbReadDWORDTag(pdb, tag)
        tag = sdb_reader.SdbFindFirstTag(pdb, root, _TAG_GUEST_TARGET_PLATFORM)
        if tag != sdb_reader.TAGID_NULL:
            guest = sdb_reader.SdbReadDWORDTag(pdb, tag)
        else:
            guest = 0x1
    platform = 0
    for guest_bit, host_bit in _GUEST_TO_AMD64_HOST.items():
        if guest & guest_bit:
            platform |= host_bit
    return platform


def get_info(file_name: str | os.PathLike) -> DatabaseInformation:
    pdb = sdb_reader.SdbOpenDatabase(os.fspath(file_name))
    if pdb is None:
        raise ValueError(f"Failed to get database information for '{file_name}'")

    flags = _DB_INFO_FLAGS_BASE
    id_value = None
    if pdb.database_id is not None:
        flags |= DB_INFO_FLAGS_VALID_GUID
        id_value = UUID(bytes_le=pdb.database_id)

    return DatabaseInformation(
        Description=pdb.database_name or None,
        dwMajor=pdb.major,
        dwMinor=pdb.minor,
        dwFlags=flags,
        Id=id_value,
        dwRuntimePlatform=_runtime_platform(pdb),
    )

from pathlib import Path

import pytest
from sdbtool.info import get_info, DatabaseInformation
from uuid import UUID

TESTDATA_FOLDER = Path(__file__).parent / "data"


def test_info():
    db_info = get_info(TESTDATA_FOLDER / "app_x32.sdb")

    assert isinstance(db_info, DatabaseInformation)
    assert db_info.Description == "app_x32"
    assert db_info.dwMajor == 2
    assert db_info.dwMinor == 3
    assert db_info.dwFlags == 0x10000001
    assert db_info.Id == UUID("83964529-0dd6-4e42-b291-bfd0faa747e9")
    assert db_info.dwRuntimePlatform == 4

    # Test with a file that has no id / description:
    db_info = get_info(TESTDATA_FOLDER / "all_tagtypes.sdb")
    assert isinstance(db_info, DatabaseInformation)
    assert db_info.Description is None
    assert db_info.dwMajor == 3
    assert db_info.dwMinor == 0
    assert db_info.dwFlags == 0x10000000
    assert db_info.Id is None
    assert db_info.dwRuntimePlatform == 4

    with pytest.raises(ValueError, match="Failed to get database information for"):
        get_info(TESTDATA_FOLDER / "nonexistent.sdb")


def test_info_runtime_platform_legacy_guest():
    # app_x64.sdb is a version-2 database: apphelp ignores its RUNTIME_PLATFORM (0x4021) tag and derives dwRuntimePlatform from GUEST_TARGET_PLATFORM (0x4023 == AMD64),
    # which maps to AMD64 (0x2) on an amd64 host.
    db_info = get_info(TESTDATA_FOLDER / "app_x64.sdb")
    assert db_info.dwMajor == 2
    assert db_info.dwRuntimePlatform == 2


def test_info_runtime_platform_v3_verbatim(tmp_path):
    # A version-3 database with a RUNTIME_PLATFORM (0x4021) tag: apphelp reports
    # that value unmodified. 0x82 has no guest->host mapping, so the guest-derived
    # path would give 0 - reading back 0x82 proves the verbatim path is taken.
    import struct

    child = struct.pack("<HI", 0x4021, 0x82)  # RUNTIME_PLATFORM = AMD64 | AMD64_ON_ARM64
    database = struct.pack("<HI", 0x7001, len(child)) + child
    f = tmp_path / "v3_runtime.sdb"
    f.write_bytes(struct.pack("<II", 3, 0) + b"sdbf" + database)
    db_info = get_info(f)
    assert db_info.dwMajor == 3
    assert db_info.dwRuntimePlatform == 0x82


def test_info_header_only(tmp_path):
    # A header-only database has no DATABASE tag: runtime platform defaults to 4.
    import struct

    f = tmp_path / "header_only.sdb"
    f.write_bytes(struct.pack("<I", 2) + struct.pack("<I", 0) + b"sdbf")
    db_info = get_info(f)
    assert db_info.Description is None
    assert db_info.Id is None
    assert db_info.dwFlags == 0x10000000
    assert db_info.dwRuntimePlatform == 4

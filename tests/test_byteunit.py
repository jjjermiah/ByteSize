import pytest

from PyByteSize.byteunit import (
    ByteUnit,
    UnknownUnitError,
    find_closest_match,
    lookup_unit,
)


def test_byteunit_enum():
    # Test metric units
    assert ByteUnit.B.factor == 1
    assert ByteUnit.KB.factor == 1000
    assert ByteUnit.MB.factor == 1000**2
    assert ByteUnit.GB.factor == 1000**3
    assert ByteUnit.TB.factor == 1000**4
    assert ByteUnit.PB.factor == 1000**5
    assert ByteUnit.EB.factor == 1000**6
    assert ByteUnit.ZB.factor == 1000**7
    assert ByteUnit.YB.factor == 1000**8

    # Test binary units
    assert ByteUnit.KiB.factor == 1024
    assert ByteUnit.MiB.factor == 1024**2
    assert ByteUnit.GiB.factor == 1024**3
    assert ByteUnit.TiB.factor == 1024**4
    assert ByteUnit.PiB.factor == 1024**5
    assert ByteUnit.EiB.factor == 1024**6
    assert ByteUnit.ZiB.factor == 1024**7
    assert ByteUnit.YiB.factor == 1024**8


def test_lookup_unit():
    # Test base unit
    assert lookup_unit("B") == ByteUnit.B
    assert lookup_unit("bytes") == ByteUnit.B

    # Test metric units
    assert lookup_unit("KB") == ByteUnit.KB
    assert lookup_unit("kilobytes") == ByteUnit.KB
    assert lookup_unit("MB") == ByteUnit.MB
    assert lookup_unit("megabytes") == ByteUnit.MB
    assert lookup_unit("GB") == ByteUnit.GB
    assert lookup_unit("gigabytes") == ByteUnit.GB
    assert lookup_unit("TB") == ByteUnit.TB
    assert lookup_unit("terabytes") == ByteUnit.TB
    assert lookup_unit("PB") == ByteUnit.PB
    assert lookup_unit("petabytes") == ByteUnit.PB
    assert lookup_unit("EB") == ByteUnit.EB
    assert lookup_unit("exabytes") == ByteUnit.EB
    assert lookup_unit("ZB") == ByteUnit.ZB
    assert lookup_unit("zettabytes") == ByteUnit.ZB
    assert lookup_unit("YB") == ByteUnit.YB
    assert lookup_unit("yottabytes") == ByteUnit.YB

    # Test binary units
    assert lookup_unit("KiB") == ByteUnit.KiB
    assert lookup_unit("kibibytes") == ByteUnit.KiB
    assert lookup_unit("MiB") == ByteUnit.MiB
    assert lookup_unit("mebibytes") == ByteUnit.MiB
    assert lookup_unit("GiB") == ByteUnit.GiB
    assert lookup_unit("gibibytes") == ByteUnit.GiB
    assert lookup_unit("TiB") == ByteUnit.TiB
    assert lookup_unit("tebibytes") == ByteUnit.TiB
    assert lookup_unit("PiB") == ByteUnit.PiB
    assert lookup_unit("pebibytes") == ByteUnit.PiB
    assert lookup_unit("EiB") == ByteUnit.EiB
    assert lookup_unit("exbibytes") == ByteUnit.EiB
    assert lookup_unit("ZiB") == ByteUnit.ZiB
    assert lookup_unit("zebibytes") == ByteUnit.ZiB
    assert lookup_unit("YiB") == ByteUnit.YiB
    assert lookup_unit("yobibytes") == ByteUnit.YiB


def test_lookup_unit_unknown():
    with pytest.raises(UnknownUnitError):
        lookup_unit("unknown_unit")


def test_byteunite_str():
    assert str(ByteUnit.B) == "B"
    assert str(ByteUnit.KB) == "KB"
    assert str(ByteUnit.MB) == "MB"
    assert str(ByteUnit.GB) == "GB"
    assert str(ByteUnit.TB) == "TB"
    assert str(ByteUnit.PB) == "PB"
    assert str(ByteUnit.EB) == "EB"
    assert str(ByteUnit.ZB) == "ZB"
    assert str(ByteUnit.YB) == "YB"

    assert str(ByteUnit.KiB) == "KiB"
    assert str(ByteUnit.MiB) == "MiB"
    assert str(ByteUnit.GiB) == "GiB"
    assert str(ByteUnit.TiB) == "TiB"
    assert str(ByteUnit.PiB) == "PiB"
    assert str(ByteUnit.EiB) == "EiB"
    assert str(ByteUnit.ZiB) == "ZiB"
    assert str(ByteUnit.YiB) == "YiB"


def test_find_closest_match():
    # Test exact matches
    assert find_closest_match("KB") == "KB"
    assert find_closest_match("kilobytes") == "kilobytes"
    assert find_closest_match("MiB") == "MiB"
    assert find_closest_match("mebibytes") == "mebibytes"

    # Test close matches

    # Test finding 3 closest matches
    assert find_closest_match("kilobyte") == "kilobytes"
    assert find_closest_match("kilbyte") == "kilobytes"

    # Test additional close matches
    assert find_closest_match("megabites") == "megabytes"
    assert find_closest_match("gibibyte") == "gibibytes"
    assert find_closest_match("terabite") == "terabytes"
    assert find_closest_match("kibibite") == "kibibytes"
    assert find_closest_match("exabite") == "exabytes"
    assert find_closest_match("zebibyte") == "zebibytes"
    assert find_closest_match("yobibyte") == "yobibytes"
    assert find_closest_match("kilobyte") == "kilobytes"
    assert find_closest_match("megabyte") == "megabytes"
    assert find_closest_match("gigabyte") == "gigabytes"
    assert find_closest_match("terabyte") == "terabytes"
    assert find_closest_match("petabyte") == "petabytes"
    assert find_closest_match("exabyte") == "exabytes"
    assert find_closest_match("zettabyte") == "zettabytes"
    assert find_closest_match("yottabyte") == "yottabytes"

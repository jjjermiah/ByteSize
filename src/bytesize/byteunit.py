"""
Demonstrates using both an Enum (ByteUnit) to represent official byte units
and a read-only dictionary (SYNONYMS) for flexible string lookups, including
long-form names like “kilobytes”, “megabytes”, “kibibytes”, etc.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from types import MappingProxyType
from typing import Final, Mapping

__all__ = [
    'ByteUnit',
    'SYNONYMS',
    'METRIC_UNITS',
    'BINARY_UNITS',
    'UnknownUnitError',
    'find_closest_match',
    'lookup_unit',
]


class UnknownUnitError(KeyError):
    """
    A custom exception indicating the unit string is not recognized
    in the SYNONYMS mapping.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


# given a string (i.e "PIB"), which doesnt exist
# in the SYNONYMS dictionary, we will find similar
# strings in the dictionary and return the closest match
def find_closest_match(string: str) -> str:
    """
    Find the closest matching key(s) in the SYNONYMS mapping for the given string.

    Uses difflib.get_close_matches to suggest up to 3 possible unit keys that are
    similar to the given input. If multiple close matches are found, they are
    returned in a comma-separated list.

    Parameters
    ----------
    string : str
        The string to find a close match for.

    Returns
    -------
    str
        A comma-separated string of up to 3 closest matching keys in the SYNONYMS
        mapping. If no matches are found, returns an empty string.

    Examples
    --------
    1) A misspelling of 'kibibytes':
    >>> find_closest_match('kibyte')
    'kibibytes'

    2) A partial or incorrect prefix for binary units:
    >>> find_closest_match('PIB')
    'PiB'

    3) Confusing metric and binary units:
    >>> find_closest_match('mekabytes')
    'megabytes, MB'

    4) Another small typo, demonstrating multiple suggestions:
    >>> find_closest_match('gibibte')
    'GiB, gibibytes'

    5) Input far from any known unit (may yield no matches):
    >>> find_closest_match('kilopounds')
    ''  # an empty string if no suggestions are close enough
    """
    from difflib import get_close_matches

    def pluralized(s: str) -> str:
        return s + 's'

    if string in SYNONYMS:
        return string
    elif pluralized(string) in SYNONYMS:
        return pluralized(string)

    return ', '.join(get_close_matches(string, SYNONYMS.keys(), n=1, cutoff=0.3))


@lru_cache(maxsize=64)
def lookup_unit(unit_str: str) -> ByteUnit:
    """
    Look up the corresponding ByteUnit enum member for the given unit_str.
    Uses an LRU cache to speed up repeated lookups.

    Parameters
    ----------
    unit_str : str
        A string representing a known byte unit, e.g. "MB", "gigabytes", "KiB".

    Returns
    -------
    ByteUnit
        The ByteUnit enum member corresponding to the string.

    Raises
    ------
    UnknownUnitError
        If the string does not match any key in the SYNONYMS mapping.
    """
    try:
        return SYNONYMS[unit_str]
    except KeyError as exc:
        msg = f"No matching byte unit for '{unit_str}'"
        raise UnknownUnitError(msg) from exc


class ByteUnit(Enum):
    """
    Enum representing official byte units, both metric and binary.

    Attributes
    ----------
    factor : int
        Numeric multiplier from bytes.
    """

    B = 1
    KB = 1_000
    MB = 1_000_000
    GB = 1_000_000_000
    TB = 1_000_000_000_000
    PB = 1_000_000_000_000_000
    EB = 1_000_000_000_000_000_000
    ZB = 1_000_000_000_000_000_000_000
    YB = 1_000_000_000_000_000_000_000_000

    KiB = 1_024
    MiB = 1_048_576
    GiB = 1_073_741_824
    TiB = 1_099_511_627_776
    PiB = 1_125_899_906_842_624
    EiB = 1_152_921_504_606_846_976
    ZiB = 1_180_591_620_717_411_303_424
    YiB = 1_208_925_819_614_629_174_706_176

    def __init__(self, factor: int) -> None:
        """
        Parameters
        ----------
        factor : int
            Numeric multiplier from the base unit (bytes).
        """
        self.factor: int = factor

    def __str__(self) -> str:
        return self.name


#: A read-only dictionary mapping common string forms (short and spelled-out) to ByteUnit.
#: Extend as needed. Each key should map uniquely to a ByteUnit.
SYNONYMS: Mapping[str, ByteUnit] = MappingProxyType(
    {
        # Base unit
        'B': ByteUnit.B,
        'bytes': ByteUnit.B,
        # Metric units
        'KB': ByteUnit.KB,
        'kilobytes': ByteUnit.KB,
        'MB': ByteUnit.MB,
        'megabytes': ByteUnit.MB,
        'GB': ByteUnit.GB,
        'gigabytes': ByteUnit.GB,
        'TB': ByteUnit.TB,
        'terabytes': ByteUnit.TB,
        'PB': ByteUnit.PB,
        'petabytes': ByteUnit.PB,
        'EB': ByteUnit.EB,
        'exabytes': ByteUnit.EB,
        'ZB': ByteUnit.ZB,
        'zettabytes': ByteUnit.ZB,
        'YB': ByteUnit.YB,
        'yottabytes': ByteUnit.YB,
        # Binary units
        'KiB': ByteUnit.KiB,
        'kibibytes': ByteUnit.KiB,
        'MiB': ByteUnit.MiB,
        'mebibytes': ByteUnit.MiB,
        'GiB': ByteUnit.GiB,
        'gibibytes': ByteUnit.GiB,
        'TiB': ByteUnit.TiB,
        'tebibytes': ByteUnit.TiB,
        'PiB': ByteUnit.PiB,
        'pebibytes': ByteUnit.PiB,
        'EiB': ByteUnit.EiB,
        'exbibytes': ByteUnit.EiB,
        'ZiB': ByteUnit.ZiB,
        'zebibytes': ByteUnit.ZiB,
        'YiB': ByteUnit.YiB,
        'yobibytes': ByteUnit.YiB,
    }
)


METRIC_UNITS: Final[tuple[ByteUnit, ...]] = (
    ByteUnit.B,
    ByteUnit.KB,
    ByteUnit.MB,
    ByteUnit.GB,
    ByteUnit.TB,
    ByteUnit.PB,
    ByteUnit.EB,
    ByteUnit.ZB,
    ByteUnit.YB,
)

BINARY_UNITS: Final[tuple[ByteUnit, ...]] = (
    ByteUnit.B,
    ByteUnit.KiB,
    ByteUnit.MiB,
    ByteUnit.GiB,
    ByteUnit.TiB,
    ByteUnit.PiB,
    ByteUnit.EiB,
    ByteUnit.ZiB,
    ByteUnit.YiB,
)

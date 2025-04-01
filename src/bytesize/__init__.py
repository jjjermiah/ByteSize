"""This is a docstring for the public package."""

from .bytesize import (
    ByteSize,
    ByteSizeError,
    InvalidNumericValueError,
    NegativeByteSizeError,
    UnrecognizedSizeStringError,
)
from .byteunit import (
    BINARY_UNITS,
    METRIC_UNITS,
    SYNONYMS,
    ByteUnit,
    UnknownUnitError,
    find_closest_match,
    lookup_unit,
)

__all__ = [
    # byteunit
    'ByteUnit',
    'SYNONYMS',
    'METRIC_UNITS',
    'BINARY_UNITS',
    'UnknownUnitError',
    'find_closest_match',
    'lookup_unit',
    # bytesize
    'ByteSize',
    'ByteSizeError',
    'NegativeByteSizeError',
    'UnrecognizedSizeStringError',
    'InvalidNumericValueError',
]
version = '0.1.0'

__version__ = version

from __future__ import annotations

import re
from typing import Type

from bytesize.byteunit import (
    BINARY_UNITS,
    METRIC_UNITS,
    ByteUnit,
    UnknownUnitError,
    find_closest_match,
    lookup_unit,
)

__all__ = [
    "ByteSize",
    "ByteSizeError",
    "NegativeByteSizeError",
    "UnrecognizedSizeStringError",
    "InvalidNumericValueError",
]


class ByteSizeError(Exception):
    """
    Base class for all ByteSize-related errors.
    """


class UnrecognizedSizeStringError(ByteSizeError):
    """Raised when a size string cannot be parsed."""


class InvalidNumericValueError(ByteSizeError):
    """
    Raised when the numeric portion of the string cannot be
    converted to a float, or is otherwise invalid.
    """


class NegativeByteSizeError(ByteSizeError):
    """
    Raised if the parsed numeric value is below zero.
    """

    def __init__(self, value: object) -> None:
        message = f"Byte size cannot be negative: {value}"
        super().__init__(message)


class ByteSize(int):
    """
    Stores a size in bytes (subclass of int).

    Provides:
      - Best-fit metric or binary representation via ByteUnit.
      - Apparent size calculations (block alignment).
      - Dynamic attribute-based unit conversions (size.MB, size.gibibytes, etc.).
      - Comprehensive string formatting via __format__.

    Examples
    --------
    >>> size = ByteSize(1_234_567)
    >>> print(size.readable_metric)
    ('MB', 1.234567)
    >>> print(size.readable_binary)
    ('MiB', 1.177...)
    >>> print(size.MB)
    1.234567
    >>> print(f'{size:.2f:GiB}')
    '0.00 GiB'
    """

    def __new__(cls, value: int | str) -> ByteSize:
        """
        Create a new ByteSize instance.

        If 'value' is a string, delegate to 'from_string' to parse
        and convert the result to an integer. Otherwise, assume 'value'
        is an integer representing raw bytes.
        """
        if isinstance(value, str):
            # Delegate to a classmethod that parses the string and returns ByteSize
            # e.g., 'from_string' => ByteSize(some_int_value)
            return cls.from_string(value)

        if value < 0:
            raise NegativeByteSizeError(value)

        # If it's a valid integer, create the instance using super().__new__
        return super().__new__(cls, value)

    def __init__(self, value: int | str) -> None:
        """
        Final initialization step.

        Sets 'self.bytes' and 'self.B' to the integer value. Note that by the
        time we reach __init__, 'self' is already an int-based object if the
        constructor used __new__. We rely on 'int(self)' to retrieve the integer.
        """
        # At this point, 'self' is an int, so we can just store it in attributes
        self.bytes = self.B = int(self)
        # No need to call super().__init__ here because for int subclasses
        # it typically does nothing, but included if you prefer consistency:
        super().__init__()

    @classmethod
    def from_string(cls: Type[ByteSize], value: str) -> ByteSize:
        """
        Parse a string like "10MB" or "1536KiB" into a ByteSize object.

        This method looks for:
        - A numeric part (integer or float).
        - An optional unit string (e.g., 'MB', 'MiB', 'gigabytes').

        If no unit is present, the value is treated as raw bytes.
        Raises UnknownUnitError if the unit is invalid, possibly providing suggestions.

        Parameters
        ----------
        value : str
            A size string, such as "10MB", "1536KiB", or "1024".

        Returns
        -------
        ByteSize
            A new ByteSize instance initialized from the parsed size.

        Examples
        --------
        >>> ByteSize.from_string('1000')
        ByteSize(1000) = 0.98 KiB

        >>> ByteSize.from_string('10MB')
        ByteSize(10000000) = 9.54 MiB

        >>> ByteSize.from_string('1536KiB')
        ByteSize(1572864) = 1.50 MiB

        >>> ByteSize.from_string('10.5MB')
        ByteSize(10500000) = 10.01 MiB

        # If unrecognized:
        >>> ByteSize.from_string('999XX')
        UnknownUnitError: "No matching byte unit for 'XX'; did you mean: MB?"
        """
        # Simple regex to capture optional decimal numeric part and optional unit
        match = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*([A-Za-z]+)?\s*$", value)
        if not match:
            msg = f"Could not parse size string: '{value}'"
            msg += "\nExpected format: '10MB', '1536KiB', or '1024'."
            raise UnrecognizedSizeStringError(msg)

        numeric_str, unit_str = match.groups()

        # Convert to float
        numeric_val = float(numeric_str)

        if numeric_val < 0:
            raise NegativeByteSizeError(numeric_val)

        # Default to raw bytes if no unit is specified
        if not unit_str:
            return cls(int(numeric_val))

        # Otherwise, look up the unit in SYNONYMS
        try:
            bu = lookup_unit(unit_str)
        except UnknownUnitError as exc:
            # Provide suggestions (if any)
            suggestions = find_closest_match(unit_str)
            msg = f"Unrecognized unit '{unit_str}';"
            msg += f" did you mean: {suggestions}?" if suggestions else ""
            raise UnknownUnitError(msg) from exc

        # Convert from float in the given unit to raw bytes
        total_bytes = int(numeric_val * bu.factor)
        return cls(total_bytes)

    def __repr__(self) -> str:
        """
        Returns a string representation of the ByteSize object.

        Examples
        --------
        >>> repr(ByteSize(1073741824))
        'ByteSize(1073741824) = 1.00 GiB'
        """
        return f"{self.__class__.__name__}({int(self)}) = {self:.2f}"

    def __str__(self) -> str:
        """
        Returns a string representation using best-fit binary units.

        Examples
        --------
        >>> str(ByteSize(1073741824))
        '1.00 GiB'
        """
        return self.__format__(".2f")

    # -------------------------------------------------------------------
    #  Best-fit logic
    # -------------------------------------------------------------------
    @property
    def readable_metric(self) -> tuple[str, float]:
        """
        Returns the best-fit metric unit and its scaled value.

        Returns
        -------
        tuple[str, float]
            A tuple containing the best metric suffix and the scaled value.

        Examples
        --------
        >>> ByteSize(1_234_567).readable_metric
        ('MB', 1.234567)
        """
        return self._best_fit(METRIC_UNITS, base=1000)

    @property
    def readable_binary(self) -> tuple[str, float]:
        """
        Returns the best-fit binary unit and its scaled value.

        Returns
        -------
        tuple[str, float]
            A tuple containing the best binary suffix and the scaled value.

        Examples
        --------
        >>> ByteSize(1_234_567).readable_binary
        ('MiB', 1.18)
        """
        return self._best_fit(BINARY_UNITS, base=1024)

    def _best_fit(
        self,
        unit_list: tuple[ByteUnit, ...],
        base: int,
    ) -> tuple[str, float]:
        """
        Finds the largest ByteUnit in 'unit_list' such that
        'self.bytes / unit.factor' is < base (or we hit the last unit).
        Returns (unit_string, scaled_float).
        """
        value = int(self)
        for unit in unit_list:
            scaled = value / unit.factor
            if scaled < base:
                return (str(unit), scaled)
        return (str(unit_list[-1]), value / unit_list[-1].factor)

    # -------------------------------------------------------------------
    #  Apparent size calculation (block alignment)
    # -------------------------------------------------------------------
    def apparent_size(self, block_size: int) -> ByteSize:
        """
        Returns the block-aligned size for a given block size.

        Algorithm:
            - Add (block_size - 1) to the size to ensure rounding up.
            - Divide by block_size to get the number of blocks.

        Parameters
        ----------
        block_size : int
            The block size in bytes.

        Returns
        -------
        ByteSize
            The block-aligned size.

        Raises
        ------
        ValueError
            If the block size is less than or equal to 0.

        Examples
        --------
        >>> ByteSize(1_234_567).apparent_size(4096)
        ByteSize(1_236_992)
        """
        if block_size <= 0:
            msg = "Block size must be > 0."
            raise ValueError(msg)
        blocks = (self.bytes + block_size - 1) // block_size
        return ByteSize(blocks * block_size)

    # -------------------------------------------------------------------
    #  Dynamic attribute-based conversions
    # -------------------------------------------------------------------
    def __getattr__(self, name: str) -> float:
        """
        Allows dynamic attribute-based conversions.

        Parameters
        ----------
        name : str
            The name of the unit to convert to.

        Returns
        -------
        float
            The size in the specified unit.

        Raises
        ------
        AttributeError
            If the unit is not recognized.

        Examples
        --------
        >>> size = ByteSize(1_234_567)
        >>> size.MB
        1.234567
        >>> size.mebibytes
        1.177...
        """
        try:
            unit = lookup_unit(name)
        except UnknownUnitError as exc:
            # If no match, raise the standard Python attribute error
            msg = f"'{type(self).__name__}' object has no attribute '{name}'"
            msg += f"\nClosest matches: {find_closest_match(name)}"
            raise AttributeError(msg) from exc
        return self.bytes / unit.factor

    def to_unit(self, unit: str) -> float:
        """
        Convert the ByteSize to the specified unit.

        Parameters
        ----------
        unit : str
            The unit to convert to (e.g., 'MB', 'GiB').

        Returns
        -------
        float
            The size in the specified unit.

        Raises
        ------
        UnknownUnitError
            If the unit is not recognized.
        """
        try:
            byte_unit = lookup_unit(unit)
        except UnknownUnitError as exc:
            suggestions = find_closest_match(unit)
            msg = f"Unrecognized unit '{unit}';"
            msg += f" did you mean: {suggestions}?" if suggestions else ""
            raise UnknownUnitError(msg) from exc
        return self.bytes / byte_unit.get_factor()

    # -------------------------------------------------------------------
    #  Rich string formatting with __format__
    # -------------------------------------------------------------------
    def __format__(self, format_spec: str) -> str:
        """
        Formats the ByteSize object according to the given format specification.

        Defaults to a float format with binary units if no unit is specified.

        Parameters
        ----------
        format_spec : str
            The format specification.

        Returns
        -------
        str
            The formatted string.

        Raises
        ------
        ValueError
            If the unit in the format specification is not recognized.

        Examples
        --------
        >>> size = ByteSize(1_234_567)
        >>> sixe.MB
        1.234567
        >>> f'{size:.2f:MB}'
        '1.23 MB'
        >>> f'{size:.2f:GiB}'
        '0.00 GiB'
        """
        # Check for 'precision:unit' style, e.g. '.2f:MB'
        if ":" in format_spec:
            float_fmt, suffix = format_spec.split(":", 1)
            try:
                unit = lookup_unit(suffix)
            except UnknownUnitError as exc:
                msg = f"Unknown unit: {suffix}"
                msg += f"\nClosest matches: {find_closest_match(suffix)}"
                raise UnknownUnitError(msg) from exc
            scaled = self.bytes / unit.factor
            return f"{scaled:{float_fmt}} {suffix}"

        # If the entire format spec might be a known unit (like 'MB' or 'B'):
        try:
            unit = lookup_unit(format_spec)
            scaled = self.bytes / unit.factor
        except UnknownUnitError:
            # Not a recognized unit, so treat format_spec as a float format
            suffix, scaled = self.readable_binary
            return f"{scaled:{format_spec}} {suffix}"
        else:
            # If exactly 'B', show as an integer
            if format_spec == "B":
                return f"{scaled:.0f} B"
            return f"{scaled:.2f} {format_spec}"

    # -------------------------------------------------------------------
    #  Arithmetic returning ByteSize
    # -------------------------------------------------------------------
    def __add__(self, other: int | ByteSize) -> ByteSize:
        return ByteSize(super().__add__(other))

    def __sub__(self, other: int | ByteSize) -> ByteSize:
        result = super().__sub__(other)
        return ByteSize(result)

    def __mul__(self, other: int | ByteSize) -> ByteSize:
        return ByteSize(super().__mul__(other))

    def __truediv__(self, other: int | ByteSize) -> ByteSize:
        div_result = super().__truediv__(other)
        # Convert to int or floor to preserve whole bytes, or let it stay float?
        # The old version cast to int. We'll follow that:
        return ByteSize(int(div_result))

    def __floordiv__(self, other: int | ByteSize) -> ByteSize:
        return ByteSize(super().__floordiv__(other))

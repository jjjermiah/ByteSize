from typing import Any

import pytest

from bytecase.bytesize import (
    ByteSize,
    NegativeByteSizeError,
    UnknownUnitError,
    UnrecognizedSizeStringError,
)

DEFAULT_TOLERANCE = 1e-9


class TestByteSizeInitialization:
    """
    Demonstrates a test class using pytest with a large number
    of parameterized inputs to validate ByteSize's initialization
    from both int and str.
    """

    # A large set of valid test cases: (input_value, expected_bytes)
    #  - Either int or str
    #  - We check that ByteSize(...) produces the expected internal bytes
    # You can easily add or generate more for an "insanely large" set.
    @pytest.mark.parametrize(
        "input_value,expected",
        [
            # Integers
            (0, 0),
            (1, 1),
            (999, 999),
            (1024, 1024),
            (10_000_000, 10_000_000),
            # Some typical negative test should raise
            # We'll handle that in test_init_exceptions.
            # Strings: basic
            ("0B", 0),
            ("1B", 1),
            ("999B", 999),
            ("1024B", 1024),
            ("   1024B   ", 1024),  # with whitespace
            # Strings: MB
            ("1MB", 1_000_000),
            ("10.5MB", 10_500_000),
            # Strings: GB
            ("2GB", 2_000_000_000),
            ("2.75GB", 2_750_000_000),
            # Strings: TiB (example for binary)
            ("1TiB", 1_099_511_627_776),
            ("0.5TiB", 549_755_813_888),
        ],
    )
    def test_init_valid(self, input_value: Any, expected: int) -> None:
        """Ensure ByteSize init from int/str yields the correct internal bytes."""
        size = ByteSize(input_value)
        assert size == expected, (
            f"ByteSize({input_value}) produced {size}, expected {expected}"
        )
        assert size.bytes == expected

    def test_edge_case_from_str(self) -> None:
        """
        Test edge case where the input string is a number
        that is too large to be represented as an int.
        """
        size = ByteSize("1208925819614629174706176")
        assert size.bytes == 1_208_925_819_614_629_174_706_176

    # A large set of invalid or edge-case test cases
    @pytest.mark.parametrize(
        "input_value,exc_type",
        [
            (-1, NegativeByteSizeError),  # negative int
            ("-100B", NegativeByteSizeError),  # negative string
            ("not_a_number", UnrecognizedSizeStringError),  # parse error
            ("", UnrecognizedSizeStringError),  # empty
            ("   ", UnrecognizedSizeStringError),  # whitespace only
            ("999XX", UnknownUnitError),  # unknown unit
        ],
    )
    def test_init_exceptions(self, input_value: Any, exc_type: type[Exception]) -> None:
        """
        Test invalid scenarios that should raise an exception.
        """
        with pytest.raises(exc_type):
            _ = ByteSize(input_value)


class TestByteSizeBestFit:
    """
    Tests for the best-fit logic of ByteSize.
    """

    @pytest.mark.parametrize(
        "input_value,expected_metric,expected_binary",
        [
            (1_234_567, ("MB", 1.234567), ("MiB", 1.1773748397827148)),
            (1_000_000_000, ("GB", 1.0), ("MiB", 953.67431640625)),
            (1_099_511_627_776, ("TB", 1.099511627776), ("TiB", 1.0)),
        ],
    )
    def test_best_fit(
        self,
        input_value: int,
        expected_metric: tuple[str, float],
        expected_binary: tuple[str, float],
    ) -> None:
        size = ByteSize(input_value)
        assert size.readable_metric == (
            expected_metric[0],
            pytest.approx(expected_metric[1], abs=DEFAULT_TOLERANCE),
        )
        assert size.readable_binary == (
            expected_binary[0],
            pytest.approx(expected_binary[1], abs=DEFAULT_TOLERANCE),
        )

    def test_edge(self) -> None:
        size = ByteSize(1_208_925_819_614_629_174_706_176) * 1025

        # print(size
        assert size.readable_binary == ("YiB", 1025.0)
        assert size.readable_metric == pytest.approx(
            ("YB", 1239.148965104), abs=DEFAULT_TOLERANCE
        )


class TestByteSizeApparentSize:
    """
    Tests for the apparent size calculation of ByteSize.
    """

    @pytest.mark.parametrize(
        "input_value,block_size,expected",
        [
            (1_234_567, 4096, 1_236_992),
            (1_000_000, 512, 1000448),
            (1_000_000, 1024, 1000448),
            (1_000_000, 2048, 1_001_472),
        ],
    )
    def test_apparent_size(
        self, input_value: int, block_size: int, expected: int
    ) -> None:
        size = ByteSize(input_value)
        assert size.apparent_size(block_size) == ByteSize(expected)

    def test_apparent_size_invalid(self) -> None:
        size = ByteSize(1_000_000)
        with pytest.raises(ValueError):
            _ = size.apparent_size(0)


class TestByteSizeDynamicAttributes:
    """
    Tests for the dynamic attribute-based conversions of ByteSize.
    """

    @pytest.mark.parametrize(
        "input_value,attribute,expected",
        [
            (1_234_567, "MB", 1.234567),
            (1_234_567, "MiB", 1.1773748397827148),
            (1_000_000_000, "GB", 1.0),
            (1_000_000_000, "GiB", 0.9313225746154785),
        ],
    )
    def test_dynamic_attributes(
        self, input_value: int, attribute: str, expected: float
    ) -> None:
        size = ByteSize(input_value)
        assert getattr(size, attribute) == pytest.approx(
            expected, abs=DEFAULT_TOLERANCE
        )

    def test_dynamic_attributes_invalid(self) -> None:
        size = ByteSize(1_000_000)
        with pytest.raises(AttributeError):
            _ = size.invalid_attribute


class TestByteSizeFormat:
    """
    Tests for the rich string formatting of ByteSize.
    """

    @pytest.mark.parametrize(
        "input_value,format_spec,expected",
        [
            (1_234_567, ".2f:MB", "1.23 MB"),
            (1_234_567, ".2f:MiB", "1.18 MiB"),
            (1_000_000_000, ".2f:GB", "1.00 GB"),
            (1_000_000_000, ".2f:GiB", "0.93 GiB"),
            # only our format spec
            (1_000_000_000, ".2f", "953.67 MiB"),
            # only the unit
            (1_000_000_000, "GB", "1.00 GB"),
            (1_000_000_000, "B", "1000000000 B"),
        ],
    )
    def test_format(self, input_value: int, format_spec: str, expected: str) -> None:
        size = ByteSize(input_value)
        assert format(size, format_spec) == expected

    def test_format_invalid(self) -> None:
        size = ByteSize(1_000_000)
        with pytest.raises(UnknownUnitError):
            _ = format(size, ".2f:invalid_format_spec")

    def test_str(self) -> None:
        size = ByteSize(1_000_000)
        assert str(size) == "976.56 KiB"


class TestByteSizeArithmetic:
    """
    Tests for arithmetic operations returning ByteSize.
    """

    def test_addition(self) -> None:
        size1 = ByteSize(1_000_000)
        size2 = ByteSize(2_000_000)
        assert size1 + size2 == ByteSize(3_000_000)

    def test_subtraction(self) -> None:
        size1 = ByteSize(3_000_000)
        size2 = ByteSize(1_000_000)
        assert size1 - size2 == ByteSize(2_000_000)

    def test_multiplication(self) -> None:
        size = ByteSize(1_000_000)
        assert size * 2 == ByteSize(2_000_000)

    def test_division(self) -> None:
        size = ByteSize(2_000_000)
        assert size / 2 == ByteSize(1_000_000)

    def test_floordiv(self) -> None:
        size = ByteSize(2_000_000)
        assert size // 2 == ByteSize(1_000_000)


if __name__ == "__main__":
    pytest.main([__file__])

"""Suite de pruebas del módulo `roman`.

Verifica los contratos definidos en `SPEC.md` §10.1: valores conocidos,
límites del rango `1..3999`, tipos de entrada, canonicalidad de los
numerales y roundtrip exhaustivo sobre los 3999 valores del rango.

Las aserciones se ejecutan siempre sobre la implementación real de
`src/roman.py`; no se usan mocks, dobles ni datos prefabricados.
"""

import re

import pytest
from roman import MAX_VALUE, MIN_VALUE, from_roman, to_roman

# Regex canónica declarada localmente en el módulo de pruebas: `src/roman.py`
# debe permanecer libre de expresiones regulares (SPEC.md §6.2).
CANONICAL_PATTERN = re.compile(
    r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
)

# Repeticiones aditivas prohibidas por la forma canónica (SPEC.md §10, req. 14).
FORBIDDEN_REPEATS = ("IIII", "VV", "XXXX", "LL", "CCCC", "DD")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, "I"),
        (2, "II"),
        (3, "III"),
        (4, "IV"),
        (5, "V"),
        (6, "VI"),
        (9, "IX"),
        (10, "X"),
        (14, "XIV"),
        (40, "XL"),
        (44, "XLIV"),
        (50, "L"),
        (90, "XC"),
        (100, "C"),
        (400, "CD"),
        (500, "D"),
        (900, "CM"),
        (1000, "M"),
        (1990, "MCMXC"),
        (2024, "MMXXIV"),
    ],
)
def test_to_roman_known_values(value, expected):
    """Codifica valores conocidos en su numeral romano canónico (SPEC.md §10.1)."""
    assert to_roman(value) == expected


def test_to_roman_bounds():
    """Verifica los extremos del rango inclusivo `1..3999` (SPEC.md §10.1)."""
    assert to_roman(MIN_VALUE) == "I"
    assert to_roman(MAX_VALUE) == "MMMCMXCIX"


@pytest.mark.parametrize("value", [0, -1, -3999, 4000, 10000])
def test_to_roman_out_of_range_raises_value_error(value):
    """Rechaza con `ValueError` los valores fuera del rango `1..3999` (SPEC.md §2.3)."""
    with pytest.raises(ValueError, match="expects 1 <= n <= 3999"):
        to_roman(value)


@pytest.mark.parametrize("value", [1.0, "1", None, [1], (1,), 3 + 0j])
def test_to_roman_non_int_raises_type_error(value):
    """Rechaza con `TypeError` toda entrada que no sea un `int` (SPEC.md §2.3)."""
    with pytest.raises(TypeError, match="expects int"):
        to_roman(value)


def test_to_roman_bool_raises_type_error():
    """Rechaza `bool` con `TypeError` aunque subclase `int` (SPEC.md §2.2)."""
    with pytest.raises(TypeError, match="expects int, got bool"):
        to_roman(True)
    with pytest.raises(TypeError, match="expects int, got bool"):
        to_roman(False)


@pytest.mark.parametrize(
    ("numeral", "expected"),
    [
        ("I", 1),
        ("II", 2),
        ("III", 3),
        ("IV", 4),
        ("V", 5),
        ("VI", 6),
        ("IX", 9),
        ("X", 10),
        ("XIV", 14),
        ("XL", 40),
        ("XLIV", 44),
        ("L", 50),
        ("XC", 90),
        ("C", 100),
        ("CD", 400),
        ("D", 500),
        ("CM", 900),
        ("M", 1000),
        ("MCMXC", 1990),
        ("MMXXIV", 2024),
        ("MMMCMXCIX", 3999),
    ],
)
def test_from_roman_known_values(numeral, expected):
    """Decodifica numerales conocidos a su valor entero (SPEC.md §10.1)."""
    assert from_roman(numeral) == expected


@pytest.mark.parametrize(
    ("numeral", "expected"),
    [
        ("mcmxc", 1990),
        ("McMxC", 1990),
        ("MmCmXc", 2990),
        ("iv", 4),
        ("mmmcmxcix", 3999),
    ],
)
def test_from_roman_accepts_lowercase_and_mixed_case(numeral, expected):
    """Normaliza con `upper()` y acepta minúsculas y mayúsculas mixtas (SPEC.md §2.2)."""
    # "McMxC" normaliza a "MCMXC" (1990) y "MmCmXc" normaliza a "MMCMXC" (2990):
    # el valor devuelto es siempre el del numeral normalizado.
    assert from_roman(numeral) == expected


def test_from_roman_empty_string_raises_value_error():
    """Rechaza con `ValueError` la cadena vacía (SPEC.md §2.3)."""
    with pytest.raises(ValueError, match="non-empty"):
        from_roman("")


@pytest.mark.parametrize(
    "numeral",
    [
        "IIII",
        "VV",
        "IC",
        "MMMM",
        "XXXX",
        "LC",
        "DM",
        "IL",
        "VX",
        "IIX",
        "CCCC",
        "DD",
        "LL",
    ],
)
def test_from_roman_non_canonical_raises_value_error(numeral):
    """Rechaza con `ValueError` los numerales no canónicos (SPEC.md §2.3)."""
    with pytest.raises(ValueError, match="not a canonical Roman numeral"):
        from_roman(numeral)


@pytest.mark.parametrize("numeral", ["ABC", "XII3", "X I", "roman"])
def test_from_roman_invalid_characters_raise_value_error(numeral):
    """Rechaza con `ValueError` los caracteres ajenos a `MDCLXVI` (SPEC.md §2.3)."""
    with pytest.raises(ValueError, match="invalid character"):
        from_roman(numeral)


@pytest.mark.parametrize("value", [None, 4, b"IV", ["I"]])
def test_from_roman_non_str_raises_type_error(value):
    """Rechaza con `TypeError` toda entrada que no sea un `str` (SPEC.md §2.3)."""
    with pytest.raises(TypeError, match="expects str"):
        from_roman(value)


def test_roundtrip_all_values_1_to_3999():
    """Verifica el roundtrip sobre los 3999 valores de `1..3999` (SPEC.md §2.4)."""
    for n in range(MIN_VALUE, MAX_VALUE + 1):
        numeral = to_roman(n)
        assert isinstance(numeral, str)
        assert from_roman(numeral) == n
        assert to_roman(from_roman(numeral)) == numeral
        assert from_roman(numeral.lower()) == n
        for repetition in FORBIDDEN_REPEATS:
            assert repetition not in numeral, f"{numeral} contiene la repetición {repetition}"


def test_canonical_regex_conformance():
    """Comprueba que toda salida cumple la regex canónica (SPEC.md §10.1)."""
    for n in range(MIN_VALUE, MAX_VALUE + 1):
        numeral = to_roman(n)
        assert CANONICAL_PATTERN.fullmatch(numeral), f"{numeral} no es canónico para {n}"

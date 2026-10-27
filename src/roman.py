"""Conversión entre enteros y numerales romanos en notación canónica.

El módulo expone dos funciones puras y deterministas:

- :func:`to_roman` codifica un entero (``1..3999``) como numeral romano.
- :func:`from_roman` decodifica un numeral romano (mayúsculas o minúsculas).

La notación sustractiva (IV, IX, XL, XC, CD, CM) se define en
:data:`NUMERAL_TABLE`, que es la única fuente de verdad del módulo. La
canonicalidad de una entrada se valida re-codificando su valor, de modo que no
se requiere expresiones regulares ni dependencias externas.
"""

from typing import List, Tuple

__all__ = [
    "to_roman",
    "from_roman",
    "MIN_VALUE",
    "MAX_VALUE",
    "NUMERAL_TABLE",
    "VALID_NUMERAL_CHARS",
]

MIN_VALUE: int = 1
MAX_VALUE: int = 3999

# Tabla de numerales ordenada de mayor a menor; cada entrada es
# (valor_entero, numeral). Los pares sustractivos forman parte de la tabla,
# por lo que el codificado greedy nunca produce "IIII", "VIIII", "XXXX", etc.
NUMERAL_TABLE: List[Tuple[int, str]] = [
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
]

VALID_NUMERAL_CHARS: str = "MDCLXVI"


def _validate_int_input(n: int) -> None:
    """Valida el tipo y el rango del entero recibido por :func:`to_roman`.

    Args:
        n: Valor a validar.

    Raises:
        TypeError: Si ``n`` no es un ``int`` o es un ``bool``.
        ValueError: Si ``n`` está fuera del rango ``1..3999``.
    """
    # El chequeo de bool va primero: bool es subclase de int y no debe aceptarse.
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError(f"to_roman() expects int, got {type(n).__name__}")
    if n < MIN_VALUE or n > MAX_VALUE:
        raise ValueError(f"to_roman() expects 1 <= n <= 3999, got {n}")


def _encode(n: int) -> str:
    """Codifica un entero válido como numeral romano canónico.

    Recorre :data:`NUMERAL_TABLE` de mayor a menor y agrega cada numeral
    mientras el resto lo permita.

    Args:
        n: Entero en el rango ``1..3999``.

    Returns:
        Numeral romano en mayúsculas y forma sustractiva.
    """
    remaining = n
    parts: List[str] = []
    for value, numeral in NUMERAL_TABLE:
        while remaining >= value:
            parts.append(numeral)
            remaining -= value
    return "".join(parts)


def _decode(upper: str) -> int:
    """Decodifica un numeral romano ya normalizado en mayúsculas.

    Recorre la cadena de izquierda a derecha: en cada posición toma el token
    de dos caracteres si existe en :data:`NUMERAL_TABLE`; si no, toma el de un
    solo carácter.

    Args:
        upper: Numeral romano en mayúsculas, con caracteres válidos.

    Returns:
        Valor entero correspondiente al numeral.
    """
    lookup = {numeral: value for value, numeral in NUMERAL_TABLE}
    total = 0
    index = 0
    while index < len(upper):
        pair = upper[index : index + 2]
        if len(pair) == 2 and pair in lookup:
            total += lookup[pair]
            index += 2
            continue
        total += lookup[upper[index]]
        index += 1
    return total


def to_roman(n: int) -> str:
    """Convierte un entero en su numeral romano canónico.

    Args:
        n: Entero a convertir, en el rango inclusivo ``1..3999``.

    Returns:
        Numeral romano en mayúsculas con notación sustractiva
        (por ejemplo, ``4`` produce ``"IV"``).

    Raises:
        TypeError: Si ``n`` no es un ``int`` o es un ``bool``.
        ValueError: Si ``n`` está fuera del rango ``1..3999``.

    Example:
        >>> to_roman(1990)
        'MCMXC'
        >>> to_roman(3999)
        'MMMCMXCIX'
    """
    _validate_int_input(n)
    return _encode(n)


def from_roman(s: str) -> int:
    """Convierte un numeral romano canónico en su valor entero.

    Acepta mayúsculas, minúsculas y mayúsculas/minúsculas combinadas. La
    entrada se normaliza con :meth:`str.upper` antes de validarse.

    Args:
        s: Numeral romano a convertir.

    Returns:
        Valor entero del numeral, siempre en el rango ``1..3999``.

    Raises:
        TypeError: Si ``s`` no es un ``str``.
        ValueError: Si ``s`` está vacía, contiene caracteres no válidos,
            no es una representación canónica (por ejemplo ``"IIII"``, ``"VV"``,
            ``"IC"``, ``"MMMM"``) o su valor queda fuera del rango ``1..3999``.

    Example:
        >>> from_roman("mcmxc")
        1990
        >>> from_roman("MMMCMXCIX")
        3999
    """
    if not isinstance(s, str):
        raise TypeError(f"from_roman() expects str, got {type(s).__name__}")
    upper = s.upper()
    if not upper:
        raise ValueError("from_roman() expects a non-empty Roman numeral string")
    for ch in upper:
        if ch not in VALID_NUMERAL_CHARS:
            raise ValueError(f"from_roman() invalid character {ch!r} in {s!r}")
    value = _decode(upper)
    try:
        canonical = to_roman(value)
    except ValueError:
        raise ValueError(f"from_roman() {s!r} is not a canonical Roman numeral") from None
    if canonical != upper:
        raise ValueError(f"from_roman() {s!r} is not a canonical Roman numeral")
    return value

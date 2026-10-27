# roman

Conversión entre enteros y numerales romanos en notación canónica sustractiva.

Librería Python mínima, escrita solo con la biblioteca estándar: `to_roman(n)` convierte un entero del rango `1..3999` en su numeral romano y `from_roman(s)` decodifica un numeral romano canónico. El paquete declara `dependencies = []`, por lo que no tiene dependencias de runtime: instalarlo no descarga bibliotecas adicionales.

## Requisitos

- Python 3.9 o superior.
- `pytest >= 7.0`, únicamente necesario para ejecutar la suite de pruebas.

## Instalación

Consumo como dependencia interna desde otro proyecto:

```bash
pip install .
```

Desarrollo, con instalación editable y los extras `dev` (incluyen `pytest`):

```bash
pip install -e ".[dev]"
```

## Uso

```python
from roman import to_roman, from_roman

to_roman(2024)          # "MMXXIV"
to_roman(1990)          # "MCMXC"
to_roman(4)             # "IV"
to_roman(3999)          # "MMMCMXCIX"

from_roman("mcmxc")     # 1990
from_roman("IV")        # 4
from_roman("mmmcmxcix") # 3999
```

`from_roman` normaliza la entrada con `str.upper()`, por lo que acepta minúsculas y mayúsculas combinadas (`"mcmxc"`, `"MmCmXc"` y `"MCMXC"` equivalen a `1990`).

## Rango y notación

El rango aceptado es `1..3999` (ambos extremos inclusive). La salida siempre es canónica y usa notación sustractiva: `IV`, `IX`, `XL`, `XC`, `CD` y `CM` en lugar de `IIII`, `VIIII`, `XXXX`, `CCCC`, `DCCCC` o `CM`.

| Entrada | Salida | Entrada | Salida |
|---|---|---|---|
| `1` | `I` | `14` | `XIV` |
| `4` | `IV` | `40` | `XL` |
| `9` | `IX` | `90` | `XC` |
| `44` | `XLIV` | `400` | `CD` |
| `90` | `XC` | `900` | `CM` |
| `1990` | `MCMXC` | `2024` | `MMXXIV` |
| `3999` | `MMMCMXCIX` | | |

Para todo `n` en `1..3999` se cumple `from_roman(to_roman(n)) == n`, y para todo numeral canónico `s` se cumple `to_roman(from_roman(s)) == s.upper()`.

## Comportamiento ante errores

Los mensajes son deterministas, lo que permite comprobarlos con `pytest.raises(..., match=...)`.

| Función | Condición | Excepción | Mensaje |
|---|---|---|---|
| `to_roman` | `n` no es `int` (incluye `bool`) | `TypeError` | `to_roman() expects int, got {tipo}` |
| `to_roman` | `n < 1` o `n > 3999` | `ValueError` | `to_roman() expects 1 <= n <= 3999, got {n}` |
| `from_roman` | `s` no es `str` | `TypeError` | `from_roman() expects str, got {tipo}` |
| `from_roman` | `s` vacía | `ValueError` | `from_roman() expects a non-empty Roman numeral string` |
| `from_roman` | `s` contiene un carácter fuera de `MDCLXVI` | `ValueError` | `from_roman() invalid character {c!r} in {s!r}` |
| `from_roman` | `s` no es canónica (`IIII`, `VV`, `IC`, `MMMM`, …) | `ValueError` | `from_roman() {s!r} is not a canonical Roman numeral` |

Ejemplos:

```python
to_roman(True)        # TypeError: to_roman() expects int, got bool
to_roman(0)           # ValueError: to_roman() expects 1 <= n <= 3999, got 0
to_roman(4000)        # ValueError: to_roman() expects 1 <= n <= 3999, got 4000
from_roman("")        # ValueError: from_roman() expects a non-empty Roman numeral string
from_roman("IIII")    # ValueError: from_roman() 'IIII' is not a canonical Roman numeral
from_roman("roman")   # ValueError: from_roman() invalid character 'R' in 'roman'
```

`bool` se rechaza aunque sea subclase de `int`: `True` y `False` producen `TypeError`, no `ValueError`. El espacio en blanco no se recorta, por lo que `" IV "` es un `ValueError`.

## Pruebas

Desde la raíz del repositorio:

```bash
python -m pytest
```

La suite (`tests/test_roman.py`) cubre valores conocidos, límites, tipos, canonicalidad y un roundtrip exhaustivo sobre los 3999 valores de `1..3999`.

## Contrato de import público

```python
from roman import (
    MAX_VALUE,
    MIN_VALUE,
    NUMERAL_TABLE,
    VALID_NUMERAL_CHARS,
    from_roman,
    to_roman,
)
```

| Símbolo | Tipo | Descripción |
|---|---|---|
| `to_roman` | `(n: int) -> str` | Codifica un entero `1..3999` como numeral romano canónico. |
| `from_roman` | `(s: str) -> int` | Decodifica un numeral romano canónico y devuelve su valor entero. |
| `MIN_VALUE` | `int` | `1`: valor mínimo aceptado. |
| `MAX_VALUE` | `int` | `3999`: valor máximo aceptado. |
| `NUMERAL_TABLE` | `List[Tuple[int, str]]` | Pares `(valor, numeral)` ordenados de mayor a menor; incluye los seis pares sustractivos `CM`, `CD`, `XC`, `XL`, `IX` e `IV`. |
| `VALID_NUMERAL_CHARS` | `str` | `"MDCLXVI"`: caracteres admitidos en la entrada de `from_roman`. |

`roman.__all__` es exactamente `["to_roman", "from_roman", "MIN_VALUE", "MAX_VALUE", "NUMERAL_TABLE", "VALID_NUMERAL_CHARS"]`. Importar el módulo no produce efectos secundarios: no hay E/S, estado mutable global ni caché.

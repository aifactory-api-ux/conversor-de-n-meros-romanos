# DEVELOPMENT PLAN: Conversor de Números Romanos

## 1. ARCHITECTURE OVERVIEW

**Naturaleza del proyecto:** librería Python pura, sin servidor, sin interfaz y sin dependencias de runtime. La totalidad del contrato está definido en `SPEC.md`, que actúa como fuente de verdad absoluta. Por eso este plan **no incluye** `backend/`, `frontend/`, `shared/`, `Dockerfile`, `docker-compose.yml`, `run.sh`, `.env.example` ni un ítem de "Infrastructure & Deployment": el GOAL indica explícitamente *"Solo librería estándar, sin servidor ni interfaz"* y `SPEC.md` §3, §4, §5, §7 y §9 declaran esos artefactos fuera de alcance. La estructura de carpetas genérica (`backend/`, `frontend/`) queda sustituida por la declarada en `SPEC.md` §4.

**Estructura de carpetas (SPEC.md §4 — única permitida):**

```
.
├── pyproject.toml          # PEP 621; py-modules=["roman"], package-dir={""="src"}; pytest pythonpath=["src"]
├── README.md               # Uso: instalación, ejemplos, tabla de errores, comando de test
├── .gitignore              # __pycache__/, *.pyc, .pytest_cache/, *.egg-info/, build/, dist/, .venv/
├── src/
│   └── roman.py            # MIN_VALUE, MAX_VALUE, NUMERAL_TABLE, VALID_NUMERAL_CHARS, to_roman(), from_roman()
└── tests/
    └── test_roman.py       # Suite pytest completa (12 funciones de test, roundtrip 1..3999)
```

**Componentes:**

| Componente | Archivo | Responsabilidad |
|---|---|---|
| Empaquetado | `pyproject.toml` | Hacer la librería consumible como dependencia interna (`pip install .`), declarar `pythonpath=["src"]` para pytest y `py-modules=["roman"]`. |
| Módulo público | `src/roman.py` | Constantes del contrato (`MIN_VALUE`, `MAX_VALUE`, `NUMERAL_TABLE`, `VALID_NUMERAL_CHARS`) y las dos funciones puras `to_roman` / `from_roman`. |
| Suite de pruebas | `tests/test_roman.py` | Verificación de valores conocidos, límites, tipos, canonicalidad y roundtrip exhaustivo 1..3999. |
| Documentación | `README.md` | Instalación, ejemplos de uso, tabla de errores y comando de ejecución de tests. |

**Contratos de datos (SPEC.md §2):**
- Constantes: `MIN_VALUE: int = 1`, `MAX_VALUE: int = 3999`, `NUMERAL_TABLE: List[Tuple[int, str]]` (13 pares ordenados de mayor a menor, incluyendo los seis pares sustractivos `CM, CD, XC, XL, IX, IV`), `VALID_NUMERAL_CHARS: str = "MDCLXVI"`.
- `to_roman(n: int) -> str`: dominio `1..3999`; `TypeError` si no es `int` o es `bool` (chequeo de `bool` **antes** del de `int`); `ValueError` fuera de rango. Codificación greedy sobre `NUMERAL_TABLE`.
- `from_roman(s: str) -> int`: normaliza con `.upper()` (acepta minúsculas y mixtas); `TypeError` si no es `str`; `ValueError` para vacías, caracteres inválidos y no canónicas (`IIII`, `VV`, `IC`, `MMMM`, …). Canonicalidad por re-codificación con `to_roman` (sin `re`).
- Mensajes de error deterministas según `SPEC.md` §2.3, para poder usar `pytest.raises(..., match=...)`.
- Invariantes: `from_roman(to_roman(n)) == n` para todo `1..3999` y `to_roman(from_roman(s)) == s.upper()`.

**Contrato de import (SPEC.md §6):** `from roman import to_roman, from_roman, MIN_VALUE, MAX_VALUE, NUMERAL_TABLE, VALID_NUMERAL_CHARS`; `__all__` exactamente con esos seis nombres; único import del módulo: `from typing import List, Tuple`. Sin `re`, `os`, `sys`, `json` ni terceros. Importar `roman` no tiene efectos secundarios (no hay bloque `__main__`).

**API / endpoints HTTP:** no aplica (SPEC.md §3). No hay puertos, ni variables de entorno, ni base de datos, ni migraciones, ni estado mutable de módulo: ambas funciones son puras y thread-safe.

**Calidad transversal (aplicada dentro de los ítems, no como ítem aparte):** type hints completos en la superficie pública, docstrings con formato Google (parámetros, retorno, excepciones, ejemplos), mensajes de error deterministas, cero placeholders (`TODO`, `pass` aislado, `NotImplementedError`), y pruebas unitarias escritas por el propio Developer (el equipo es solo el agente Developer, sin QA ni DevSec).

**Estrategia de dependencias:** `ITEM 1` es la fundación sin dependencias (empaquetado y configuración que todos consumen). `ITEM 2` crea el módulo. `ITEM 3` importa literalmente `roman` (por eso depende de ITEM 2). `ITEM 4` documenta el contrato y los comandos declarados en ITEM 1.

## 2. ACCEPTANCE CRITERIA

1. `python -m pytest` ejecutado desde la raíz del repositorio finaliza con **0 fallos, 0 errores y 0 skips**, y ejecuta las 12 funciones de test nombradas en `SPEC.md` §10.1.
2. `test_roundtrip_all_values_1_to_3999` recorre los 3999 valores y verifica `from_roman(to_roman(n)) == n`, `to_roman(from_roman(to_roman(n))) == to_roman(n)` y `from_roman(to_roman(n).lower()) == n`.
3. `to_roman(True)` y `to_roman(False)` lanzan `TypeError` con mensaje `"to_roman() expects int, got bool"`; `to_roman(0)`, `to_roman(-1)` y `to_roman(4000)` lanzan `ValueError` con `"to_roman() expects 1 <= n <= 3999"`.
4. `from_roman("")` lanza `ValueError` (`"non-empty"`); `from_roman("IIII")`, `from_roman("VV")`, `from_roman("IC")` y `from_roman("MMMM")` lanzan `ValueError` con `"is not a canonical Roman numeral"`; `from_roman("mcmxc") == 1990`.
5. `to_roman(3999) == "MMMCMXCIX"` y toda salida de `to_roman` cumple la expresión regular canónica `^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$` (regex definida solo en el módulo de test).
6. `src/roman.py` importa únicamente `typing` de la librería estándar y `pip install .` completa sin descargar dependencias de runtime.
7. `README.md` documenta `to_roman`, `from_roman`, el rango `1..3999`, la tabla de errores y el comando `python -m pytest`.
8. El repositorio **no** contiene `backend/`, `frontend/`, `Dockerfile`, `docker-compose.yml`, `run.sh`, `.env*` ni ningún archivo de servidor, base de datos o interfaz.

## TEAM SCOPE (MANDATORY — PARSED BY THE PIPELINE)

- role-dev: Developer único del proyecto — implementa librería, pruebas y documentación (sin QA ni DevSec).

## 3. EXECUTABLE ITEMS

### ITEM 1: Foundation — empaquetado PEP 621 y configuración de proyecto (`pyproject.toml`, `.gitignore`)

**Goal:** Crear la fundación que consumen todos los demás ítems: `pyproject.toml` con metadatos PEP 621 y configuración de pytest, más `.gitignore`. Claves exactas exigidas por `SPEC.md` §4.1: `[build-system] requires=["setuptools>=61"]`, `build-backend="setuptools.build_meta"`; `[project] name="roman"`, `version="0.1.0"`, `description`, `requires-python=">=3.9"`, `dependencies=[]`, `[project.optional-dependencies] dev=["pytest>=7.0"]`; `[tool.setuptools] package-dir={"" = "src"}` y `py-modules=["roman"]`; `[tool.pytest.ini_options] pythonpath=["src"]` y `testpaths=["tests"]`. El `pythonpath=["src"]` es el que permite `from roman import to_roman` en la suite sin instalación editable. `.gitignore` debe excluir `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`, `build/`, `dist/` y `.venv/`. No se crea `.env` ni `.env.example` (la librería no lee variables de entorno, `SPEC.md` §5).

**Files to create:**
- pyproject.toml (create) - metadatos PEP 621, `py-modules=["roman"]`, `package-dir={""="src"}`, extra `dev` con pytest>=7.0 y `[tool.pytest.ini_options]` con `pythonpath=["src"]` y `testpaths=["tests"]`
- .gitignore (create) - `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`, `build/`, `dist/`, `.venv/`

**Dependencies:** None

**Validation:** `python -c "import tomllib,pathlib; d=tomllib.loads(pathlib.Path('pyproject.toml').read_text()); assert d['tool']['setuptools']['py-modules']==['roman']; assert d['tool']['setuptools']['package-dir']['']=='src'; assert d['tool']['pytest']['ini_options']['pythonpath']==['src']; assert d['project']['dependencies']==[]; assert d['project']['requires-python']=='>=3.9'; print('pyproject OK')"` y `git check-ignore -v .pytest_cache/ __pycache__/x.pyc` devuelve coincidencias.

**Role:** role-dev (backend_developer)

### ITEM 2: Módulo `roman`: `to_roman` (codificación greedy sustractiva) y `from_roman` (parseo + canonicalidad por re-codificación)

**Goal:** Implementar `src/roman.py` completo — sin placeholders — con el contrato público de `SPEC.md` §2, §3 y §6. Contenido obligatorio: `from typing import List, Tuple` como único import; `__all__ = ["to_roman", "from_roman", "MIN_VALUE", "MAX_VALUE", "NUMERAL_TABLE", "VALID_NUMERAL_CHARS"]`; constantes `MIN_VALUE: int = 1`, `MAX_VALUE: int = 3999`, `NUMERAL_TABLE: List[Tuple[int, str]]` con los 13 pares ordenados de mayor a menor (`1000 M, 900 CM, 500 D, 400 CD, 100 C, 90 XC, 50 L, 40 XL, 10 X, 9 IX, 5 V, 4 IV, 1 I`) y `VALID_NUMERAL_CHARS: str = "MDCLXVI"`. Función `to_roman(n: int) -> str`: validación de tipo con el chequeo de `bool` **antes** del de `int` (`isinstance(n, bool) or not isinstance(n, int)` → `TypeError(f"to_roman() expects int, got {type(n).__name__}")`), guarda de rango (`n < MIN_VALUE or n > MAX_VALUE` → `ValueError(f"to_roman() expects 1 <= n <= 3999, got {n}")`) y bucle greedy sobre `NUMERAL_TABLE` acumulando numerales. Función `from_roman(s: str) -> int`: `TypeError(f"from_roman() expects str, got {type(s).__name__}")` si no es `str`; normalización `upper = s.upper()`; `ValueError("from_roman() expects a non-empty Roman numeral string")` si queda vacía; `ValueError(f"from_roman() invalid character {ch!r} in {s!r}")` si algún carácter no está en `VALID_NUMERAL_CHARS`; parseo greedy tomando primero el token de dos caracteres si existe en `NUMERAL_TABLE`; y validación de canonicalidad re-codificando con `to_roman(valor)` dentro de `try/except ValueError` y comparando con `upper`, lanzando `ValueError(f"from_roman() {s!r} is not a canonical Roman numeral")` en caso de discrepancia o de que la re-codificación falle (cubre `IIII`, `VV`, `IC`, `MMMM`, `XXXX`, `LC`, `DD`, etc.). Docstrings en formato Google con `Args`, `Returns`, `Raises` y `Example` en ambas funciones públicas; helpers privados prefijados con `_` (`_validate_int_input`, `_encode`, `_decode`) y también documentados. Sin `re`, sin I/O, sin estado mutable, sin bloque `__main__`.

**Files to create:**
- src/roman.py (create) - constantes del contrato, `to_roman`, `from_roman` y helpers privados `_validate_int_input`/`_encode`/`_decode`, con type hints y docstrings

**Dependencies:** Item 1

**Validation:** `python -c "import sys; sys.path.insert(0,'src'); from roman import to_roman, from_roman; assert to_roman(1)=='I' and to_roman(4)=='IV' and to_roman(1990)=='MCMXC' and to_roman(2024)=='MMXXIV' and to_roman(3999)=='MMMCMXCIX'; assert from_roman('mcmxc')==1990 and from_roman('MMMCMXCIX')==3999; [ (lambda f: f())(f) for f in [] ]; import pytest"` — y verificación de errores: `to_roman(True)`/`to_roman(0)`/`from_roman('')`/`from_roman('IIII')`/`from_roman('MMMM')` lanzan `TypeError`/`ValueError` según §2.3, y `python -c "import ast,pathlib; t=ast.parse(pathlib.Path('src/roman.py').read_text()); print([n.names[0].name for n in ast.walk(t) if isinstance(n,(ast.Import,ast.ImportFrom))])"` lista únicamente `typing`.

**Role:** role-dev (backend_developer)

### ITEM 3: Suite de pruebas pytest — `tests/test_roman.py` (12 casos + roundtrip exhaustivo 1..3999)

**Goal:** Crear `tests/test_roman.py` con imports exactos `import pytest` y `from roman import MAX_VALUE, MIN_VALUE, from_roman, to_roman`, e implementar las 12 funciones con los nombres literales de `SPEC.md` §10.1: `test_to_roman_known_values` (parametrizado: tabla completa de valores conocidos, de `1→"I"` a `2024→"MMXXIV"`), `test_to_roman_bounds` (`MIN_VALUE→"I"`, `MAX_VALUE→"MMMCMXCIX"`), `test_to_roman_out_of_range_raises_value_error` (`0`, `-1`, `-3999`, `4000`, `10000` con `match="expects 1 <= n <= 3999"`), `test_to_roman_non_int_raises_type_error` (`1.0`, `"1"`, `None`, `[1]`, `(1,)`, `3+0j` con `match="expects int"`), `test_to_roman_bool_raises_type_error` (`True`/`False` con `match="expects int, got bool"`), `test_from_roman_known_values` (inverso de la tabla, incluyendo `"IV"→4`, `"MCMXC"→1990`, `"MMMCMXCIX"→3999`), `test_from_roman_accepts_lowercase_and_mixed_case` (`"mcmxc"`, `"MmCmXc"`, `"iv"`, `"mmmcmxcix"`), `test_from_roman_empty_string_raises_value_error` (`match="non-empty"`), `test_from_roman_non_canonical_raises_value_error` (parametrizado con `"IIII"`, `"VV"`, `"IC"`, `"MMMM"` **obligatorios** más `"XXXX"`, `"LC"`, `"DM"`, `"IL"`, `"VX"`, `"IIX"`, `"CCCC"`, `"DD"`, `"LL"`, con `match="not a canonical Roman numeral"`), `test_from_roman_invalid_characters_raise_value_error` (`"ABC"`, `"XII3"`, `"X I"`, `"roman"`), `test_from_roman_non_str_raises_type_error` (`None`, `4`, `b"IV"`, `["I"]` con `match="expects str"`), `test_roundtrip_all_values_1_to_3999` (bucle `range(MIN_VALUE, MAX_VALUE + 1)` con las cuatro aserciones del §10.1) y `test_canonical_regex_conformance` (bucle `1..3999` contra la regex canónica **definida localmente en el módulo de test**, nunca en `src/roman.py`). Cada test lleva un docstring breve en español indicando qué contrato de `SPEC.md` verifica. Sin mocks ni datos falsos: todas las aserciones son sobre la implementación real.

**Files to create:**
- tests/test_roman.py (create) - 12 funciones de test con `pytest.mark.parametrize` y `pytest.raises(..., match=...)`, incluyendo roundtrip 1..3999 y conformidad con la regex canónica local

**Dependencies:** Item 1, Item 2

**Validation:** `python -m pytest -q` desde la raíz del repositorio finaliza con 0 fallos y 0 errores; `python -m pytest -q --collect-only | tail -n 5` confirma la recolección de las 12 funciones de test nombradas.

**Role:** role-dev (backend_developer)

### ITEM 4: Documentación de uso — `README.md` (instalación como dependencia interna, ejemplos y tabla de errores)

**Goal:** Crear `README.md` breve y en español que documente: descripción en una línea de la librería y su carácter de cero dependencias de runtime; instalación como dependencia interna (`pip install .` para consumo y `pip install -e ".[dev]"` para desarrollo con pytest); ejemplos de uso de `to_roman` y `from_roman` (incluyendo `to_roman(2024) == "MMXXIV"` y `from_roman("mcmxc") == 1990`); rango aceptado `1..3999` con notación sustractiva; tabla de comportamiento ante errores con las excepciones y mensajes exactos de `SPEC.md` §2.3 (`TypeError` para no `int`/`bool` y no `str`; `ValueError` para fuera de rango, vacía, carácter inválido y no canónica); comando de ejecución de pruebas `python -m pytest`; y contrato de import público (`to_roman`, `from_roman`, `MIN_VALUE`, `MAX_VALUE`, `NUMERAL_TABLE`, `VALID_NUMERAL_CHARS`). No se documenta ni se menciona ningún servidor, endpoint, Docker o variable de entorno, porque no existen.

**Files to create:**
- README.md (create) - descripción, instalación, ejemplos de `to_roman`/`from_roman`, rango 1..3999, tabla de errores y comando `python -m pytest`

**Dependencies:** Item 1

**Validation:** `python -c "import pathlib; t=pathlib.Path('README.md').read_text(encoding='utf-8'); assert all(k in t for k in ['to_roman','from_roman','1..3999','python -m pytest','TypeError','ValueError']); print('README OK', len(t))"` y revisión de que no aparecen las cadenas `Dockerfile`, `docker-compose`, `uvicorn` ni `localhost`.

**Role:** role-dev (backend_developer)
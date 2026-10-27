# SPEC.md

## 0. SCOPE SUMMARY

Build a small, dependency-free Python library that converts between integers and Roman numerals using canonical subtractive notation. The deliverable is exactly three user-facing artifacts:

1. `src/roman.py` — the module exposing `to_roman(n: int) -> str` and `from_roman(s: str) -> int`.
2. `tests/test_roman.py` — the pytest suite, including an exhaustive roundtrip test over `1..3999`.
3. `README.md` — a brief usage document.

Plus the minimal packaging file (`pyproject.toml`) required by the stated use case: *"La usará únicamente el equipo de ingeniería interno como dependencia en otros"* (the internal engineering team will consume it as a dependency in other projects).

Explicitly **out of scope** per the goal statement: *"Solo librería estándar, sin servidor ni interfaz"* — no HTTP server, no web framework, no CLI, no UI, no database, no Docker, no external services, no third-party runtime dependencies. No mocking or placeholder code will be written anywhere.

---

## 1. TECHNOLOGY STACK

| Layer | Technology | Version | Notes |
|---|---|---|---|
| Language | Python | 3.9+ (target 3.11) | Language must support `dict` insertion order and `int` subclasses — both available since 3.0; 3.9 chosen as floor because no syntax newer than 3.9 is used. |
| Runtime dependencies | *none* | — | Requirement: *"Solo librería estándar"*. Only `typing` from stdlib is imported. |
| Test framework | pytest | >= 7.0 | Required by *"Tests con pytest en tests/test_roman.py"*. `pythonpath` ini option requires pytest >= 7.0. |
| Build backend | setuptools | >= 61 | Stdlib-adjacent packaging only; needed so the module can be installed as a dependency. No third-party runtime dependency is introduced. |
| Packaging metadata | `pyproject.toml` (PEP 621) | — | Declares `roman` as an importable top-level module from the `src/` layout. |
| Lint/format | *not required* | — | Not requested; not configured. |
| CI | *not required* | — | Not requested; not configured. |

No `requirements.txt` is generated for the library itself (it has zero runtime dependencies). The only install-time tool is `pytest`, documented in `README.md` and declared in `[project.optional-dependencies] dev`.

---

## 2. DATA CONTRACTS

There is no database and no persistence. The "data contracts" for this library are its **module-level constants, type aliases, and value/error contracts**, all of which are part of the public import surface defined in §6.

### 2.1 Module constants in `src/roman.py`

```python
from typing import List, Tuple

MIN_VALUE: int = 1
MAX_VALUE: int = 3999

# Ordered high-to-low; each entry is (integer_value, numeral_string).
# This table IS the subtractive-notation rule set.
NUMERAL_TABLE: List[Tuple[int, str]] = [
    (1000, "M"),
    (900,  "CM"),
    (500,  "D"),
    (400,  "CD"),
    (100,  "C"),
    (90,   "XC"),
    (50,   "L"),
    (40,   "XL"),
    (10,   "X"),
    (9,    "IX"),
    (5,    "V"),
    (4,    "IV"),
    (1,    "I"),
]

VALID_NUMERAL_CHARS: str = "MDCLXVI"
```

### 2.2 Value type contracts

| Contract | Type | Rules |
|---|---|---|
| `n` (input to `to_roman`) | `int` | Must satisfy `isinstance(n, int)` **and** `not isinstance(n, bool)`. Accepted domain: `1 <= n <= 3999`. |
| Return of `to_roman` | `str` | Always uppercase, always canonical (matches `^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$`), always length 1–15. |
| `s` (input to `from_roman`) | `str` | Must satisfy `isinstance(s, str)`. Before validation it is normalized with `s.upper()`; the normalized form must be non-empty and canonical. Lowercase and mixed case are accepted. |
| Return of `from_roman` | `int` | Always `1 <= result <= 3999`. |
| `bool` handling | — | `bool` is a subclass of `int` in Python, so the `bool` rejection check in `to_roman` **must precede** the `int` acceptance check. `True`/`False` raise `TypeError`. |

### 2.3 Error contract (exact exception types and messages)

Every raised message is deterministic so tests can assert on `match=`.

| Function | Condition | Exception type | Exact message |
|---|---|---|---|
| `to_roman` | `n` is not an `int`, or is a `bool` | `TypeError` | `f"to_roman() expects int, got {type(n).__name__}"` |
| `to_roman` | `n < 1` or `n > 3999` | `ValueError` | `f"to_roman() expects 1 <= n <= 3999, got {n}"` |
| `from_roman` | `s` is not a `str` | `TypeError` | `f"from_roman() expects str, got {type(s).__name__}"` |
| `from_roman` | `s == ""` after `upper()` | `ValueError` | `"from_roman() expects a non-empty Roman numeral string"` |
| `from_roman` | `s` contains a character outside `MDCLXVI` (after `upper()`) | `ValueError` | `f"from_roman() invalid character {ch!r} in {s!r}"` |
| `from_roman` | `s` parses but is not canonical (`IIII`, `VV`, `IC`, `MMMM`, `XXXX`, `LC`, …) | `ValueError` | `f"from_roman() {s!r} is not a canonical Roman numeral"` |

Whitespace is **not** stripped. Any leading/trailing/internal whitespace makes the input non-canonical (or triggers the invalid-character error), which is a `ValueError`. This follows directly from *"ValueError para vacías o no canónicas"* — `" IV "` is not the canonical representation of 4.

### 2.4 Roundtrip invariants

For every `n` in `1..3999`:

```
from_roman(to_roman(n)) == n
```

For every canonical string `s` accepted by `from_roman`:

```
to_roman(from_roman(s)) == s.upper()
```

These two invariants are the complete semantic definition of the module and are both exercised by the test suite.

---

## 3. API ENDPOINTS

**There are no HTTP endpoints.** The goal states *"Solo librería estándar, sin servidor ni interfaz"* — no web framework, no ASGI/WSGI app, no `/metrics`, no webhooks, no Lambda handlers. No endpoint file, router, or server entry point exists in this project.

The complete public API surface is the programmatic one below.

### 3.1 `to_roman(n: int) -> str`

| Aspect | Contract |
|---|---|
| Import | `from roman import to_roman` |
| Parameters | `n: int` — an integer in the inclusive range `1..3999`. |
| Returns | `str` — the canonical uppercase Roman numeral for `n`, using subtractive notation for `4, 9, 40, 90, 400, 900`. |
| Raises | `TypeError` if `n` is not an `int` or is a `bool`; `ValueError` if `n` is outside `1..3999`. |
| Algorithm | Greedy left-to-right over `NUMERAL_TABLE`, subtracting the largest fitting value and appending its numeral until `n` reaches 0. The table already encodes subtractive pairs, so no special-casing is needed. |
| Complexity | O(1) — at most 15 table iterations (3999 → `MMMCMXCIX`, 9 symbols). |
| Purity | Pure function: no I/O, no global mutation, no randomness, thread-safe. |

Examples (binding): `1 → "I"`, `4 → "IV"`, `9 → "IX"`, `14 → "XIV"`, `40 → "XL"`, `90 → "XC"`, `400 → "CD"`, `900 → "CM"`, `1990 → "MCMXC"`, `2024 → "MMXXIV"`, `3999 → "MMMCMXCIX"`.

### 3.2 `from_roman(s: str) -> int`

| Aspect | Contract |
|---|---|
| Import | `from roman import from_roman` |
| Parameters | `s: str` — a Roman numeral string, uppercase, lowercase, or mixed case. |
| Returns | `int` — the integer value, in `1..3999`. |
| Raises | `TypeError` if `s` is not a `str`; `ValueError` if `s` is empty, contains an invalid character, is not canonical (`IIII`, `VV`, `IC`, `MMMM`, …), or falls outside `1..3999`. |
| Algorithm | (1) Type check → `TypeError`. (2) `upper = s.upper()`. (3) Empty check → `ValueError`. (4) Character-set check against `VALID_NUMERAL_CHARS` → `ValueError`. (5) Greedy left-to-right subtraction parse using the same `NUMERAL_TABLE`: for each position, take the two-character token if it is in the table, else the one-character token; sum. (6) Canonical validation: re-encode the parsed total with `to_roman()` inside `try/except ValueError`; if re-encoding raises or the result differs from `upper`, raise the non-canonical `ValueError`. |
| Canonicality proof | `IIII → 4 → "IV" ≠ "IIII"` → error. `VV → 10 → "X" ≠ "VV"` → error. `IC → 101 → "CI" ≠ "IC"` → error. `MMMM → 4000` → `to_roman` raises `ValueError` → converted to the non-canonical `ValueError`. |
| Complexity | O(len(s)) with len(s) ≤ 15 for accepted input. |
| Purity | Pure function: no I/O, no global mutation, thread-safe. |

### 3.3 Module-level exports

`src/roman.py` also exposes `MIN_VALUE`, `MAX_VALUE`, `NUMERAL_TABLE`, and `VALID_NUMERAL_CHARS` for consumers and tests. It defines **no** other public names; helpers are prefixed with `_` (e.g. `_validate_int_input`, `_encode`, `_decode`).

---

## 4. FILE STRUCTURE

```
.
├── pyproject.toml          # PEP 621 metadata; py-modules=["roman"], package-dir={""="src"}; pytest pythonpath=["src"]
├── README.md               # Brief usage doc: install, to_roman/from_roman examples, error behavior, test command
├── .gitignore              # __pycache__/, *.pyc, .pytest_cache/, *.egg-info/, build/, dist/, .venv/
├── src/
│   └── roman.py            # The library: NUMERAL_TABLE, MIN_VALUE, MAX_VALUE, to_roman(), from_roman()
└── tests/
    └── test_roman.py       # pytest suite: known values, bounds, type errors, canonicality, roundtrip 1..3999
```

**PORT TABLE:** Not applicable. This is a pure Python library with no network services, no containers, and no listening sockets. No port is allocated, exposed, or mapped.

**SHARED MODULES:** Not applicable. There is exactly one importable module (`roman`); there are no services and therefore no cross-service shared directory.

No `Dockerfile`, `docker-compose.yml`, `.env.example`, `run.sh`, `start.sh`, `infrastructure/`, `frontend/`, or `backend/` directory is generated — none were requested.

### 4.1 `pyproject.toml` — required keys

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "roman"
version = "0.1.0"
description = "Minimal integer <-> Roman numeral conversion (1..3999, canonical subtractive notation)."
requires-python = ">=3.9"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=7.0"]

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["roman"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

The `pythonpath = ["src"]` setting is what makes `from roman import to_roman` resolve in `tests/test_roman.py` without requiring an editable install — matching the stated layout *"src/roman.py"* and *"tests/test_roman.py"*.

---

## 5. ENVIRONMENT VARIABLES

**No environment variables are defined, read, or required.** The library performs no I/O, makes no network calls, holds no credentials, and has no configurable behavior — its entire behavior is fixed by the goal statement (range `1..3999`, subtractive notation, fixed exception types). Therefore no `.env.example` file is generated, and no `os.environ` / `os.getenv` access appears anywhere in `src/roman.py`.

| Variable | Type | Description | Example |
|---|---|---|---|
| *(none)* | — | The library is deterministic and configuration-free by design. | — |

The only environment-dependent element is the developer's Python interpreter version, which is constrained by `requires-python = ">=3.9"` in `pyproject.toml` rather than by an environment variable.

---

## 6. IMPORT CONTRACTS

### 6.1 From `src/roman.py` (importable as `roman`)

```python
from roman import to_roman            # (n: int) -> str
from roman import from_roman          # (s: str) -> int
from roman import MIN_VALUE           # int = 1
from roman import MAX_VALUE           # int = 3999
from roman import NUMERAL_TABLE       # List[Tuple[int, str]]
from roman import VALID_NUMERAL_CHARS # str = "MDCLXVI"
```

Guarantees:

* `to_roman` and `from_roman` are module-level functions, not methods — no class instantiation required.
* Importing `roman` has **no side effects** (no prints, no file access, no `__main__` execution beyond an optional `if __name__ == "__main__":` guard, which is **not** included since no CLI was requested).
* `roman.__all__` is exactly `["to_roman", "from_roman", "MIN_VALUE", "MAX_VALUE", "NUMERAL_TABLE", "VALID_NUMERAL_CHARS"]`.

### 6.2 `src/roman.py` imports

```python
from typing import List, Tuple
```

That is the complete import list. No `re`, `os`, `sys`, `json`, or third-party packages are imported. Canonicality is enforced by re-encoding (call to `to_roman`), **not** by a regular expression, keeping the validation logic in a single source of truth (`NUMERAL_TABLE`).

### 6.3 `tests/test_roman.py` imports

```python
import pytest
from roman import MAX_VALUE, MIN_VALUE, from_roman, to_roman
```

`pytest` is used for `pytest.raises`, `pytest.mark.parametrize`, and `pytest.mark.skipif` (not needed — no platform variance). No other test dependency is imported.

---

## 7. FRONTEND STATE & COMPONENT CONTRACTS

**Not applicable.** The goal explicitly excludes any interface: *"sin servidor ni interfaz"* (no server, no interface). This project contains no React/Vue/Angular/Svelte code, no hooks, no composables, no components, no props, and no browser entry point. No `frontend/` directory is created. There is consequently no shared state primitive whose property names could be consumed elsewhere.

The consumer-facing contract of this project is exclusively the Python import contract in §6.

---

## 8. FILE EXTENSION CONVENTION

* **Project language:** Python. The project is **not** JavaScript and **not** TypeScript.
* **Every source file uses the `.py` extension.** There are no `.js`, `.jsx`, `.ts`, or `.tsx` files anywhere.
* **Entry point of the library:** `src/roman.py`, imported as `from roman import to_roman, from_roman`.
* **Entry point of the test suite:** `tests/test_roman.py`, executed with `python -m pytest` from the repository root.
* There is no `index.html`, no `<script src>`, and no frontend entry point of any kind.

---

## 9. DESIGN TOKENS

**Not applicable.** No UI/UX Design Implementation Contract was supplied, and the goal excludes any interface (*"sin servidor ni interfaz"*). No `frontend/src/styles/tokens.ts`, no color/typography/spacing tokens, and no component styles exist in this project. Inventing token values here would violate scope traceability.

---

## 10. FUNCTIONAL REQUIREMENTS COVERAGE

| # | Requirement (verbatim trace to goal) | Implementation | Files |
|---|---|---|---|
| 1 | "una librería Python pequeña: `src/roman.py`" | Single module at the `src/` layout root, importable as `roman` via `py-modules=["roman"]` + `package-dir={""="src"}`. | `src/roman.py`, `pyproject.toml` |
| 2 | "`to_roman(n: int) -> str`" | Module-level function with a full type-annotated signature `def to_roman(n: int) -> str:`. | `src/roman.py` |
| 3 | Rango "1..3999" | `MIN_VALUE = 1`, `MAX_VALUE = 3999` constants; guard `if n < MIN_VALUE or n > MAX_VALUE: raise ValueError(...)`. `3999` encodes to `MMMCMXCIX`. | `src/roman.py` |
| 4 | "forma sustractiva" | `NUMERAL_TABLE` includes the six subtractive pairs `CM=900, CD=400, XC=90, XL=40, IX=9, IV=4` interleaved high-to-low; greedy encoding over that table produces `IV`, `IX`, `XL`, `XC`, `CD`, `CM` and never `IIII`, `VIIII`, `XXXX`, `CCCC`. | `src/roman.py` |
| 5 | "`ValueError` fuera de rango" | Explicit bounds guard raising `ValueError(f"to_roman() expects 1 <= n <= 3999, got {n}")` for `0`, `-1`, `4000`, `-3999`, `10**9`. | `src/roman.py`, `tests/test_roman.py::test_to_roman_out_of_range_raises_value_error` |
| 6 | "`TypeError` si no es int, incluido bool" | Order-sensitive check: `if isinstance(n, bool) or not isinstance(n, int): raise TypeError(...)`. Bool is checked first because `bool` subclasses `int`; `True`/`False` must raise `TypeError`, not be treated as `1`/`0`. Covers `float`, `str`, `None`, `list`, `Decimal`. | `src/roman.py`, `tests/test_roman.py::test_to_roman_non_int_raises_type_error`, `tests/test_roman.py::test_to_roman_bool_raises_type_error` |
| 7 | "`from_roman(s: str) -> int`" | Module-level function with a full type-annotated signature `def from_roman(s: str) -> int:`. | `src/roman.py` |
| 8 | "acepta minúsculas" | `upper = s.upper()` normalization applied before validation and parsing; `"mcmxc"`, `"MmCmXc"`, and `"MCMXC"` all return `1990`. | `src/roman.py`, `tests/test_roman.py::test_from_roman_accepts_lowercase_and_mixed_case` |
| 9 | "`ValueError` para vacías" | `if not upper: raise ValueError("from_roman() expects a non-empty Roman numeral string")`. | `src/roman.py`, `tests/test_roman.py::test_from_roman_empty_string_raises_value_error` |
| 10 | "no canónicas como IIII, VV, IC, MMMM" | Decode-then-re-encode canonicality check: `to_roman(value)` inside `try/except ValueError`; mismatch or re-encode failure → `ValueError(f"from_roman() {s!r} is not a canonical Roman numeral")`. Verified for `IIII→4≠IV`, `VV→10≠X`, `IC→101≠CI`, `MMMM→4000` (out of range). Also covers `XXXX`, `LC`, `DM`, `IL`, `VX`, `IIX`, `CCCC`, `DD`. | `src/roman.py`, `tests/test_roman.py::test_from_roman_non_canonical_raises_value_error` |
| 11 | Invalid characters → `ValueError` | Character-set scan against `VALID_NUMERAL_CHARS = "MDCLXVI"` before parsing; `"ABC"`, `"XII3"`, `"X I"`, `"Ⅻ"` → `ValueError`. (Non-canonical strings must not silently parse.) | `src/roman.py`, `tests/test_roman.py::test_from_roman_invalid_characters_raise_value_error` |
| 12 | `from_roman` non-`str` input → `TypeError` | `if not isinstance(s, str): raise TypeError(...)` — the direct consequence of the declared signature `s: str`, symmetric with requirement 6. | `src/roman.py`, `tests/test_roman.py::test_from_roman_non_str_raises_type_error` |
| 13 | "Tests con pytest en `tests/test_roman.py`" | Single pytest module using `pytest.mark.parametrize` for value tables and `pytest.raises(..., match=...)` for every documented error message. | `tests/test_roman.py` |
| 14 | "incluyendo roundtrip 1..3999" | `test_roundtrip_all_values_1_to_3999` iterates `range(MIN_VALUE, MAX_VALUE + 1)`, asserting `from_roman(to_roman(n)) == n` for all 3999 values, and asserting the encoded form matches the canonical regex and contains no forbidden repeats (`IIII`, `VV`, `XXXX`, `LL`, `CCCC`, `DD`). | `tests/test_roman.py::test_roundtrip_all_values_1_to_3999` |
| 15 | "un README breve" | `README.md` with: one-line description, zero-dependency note, install line, `to_roman`/`from_roman` usage examples, error-behavior table, and `python -m pytest` command. | `README.md` |
| 16 | "Solo librería estándar" | Zero runtime dependencies: only `from typing import List, Tuple`; `[project] dependencies = []`. No `re`, no third-party import anywhere. Verified by the absence of any non-stdlib import in `src/roman.py`. | `src/roman.py`, `pyproject.toml` |
| 17 | "sin servidor" | No `app.py`, `main.py`, FastAPI/Flask/uvicorn, no route handlers, no `/metrics`, no webhook endpoints. §3 documents this explicitly. | *(file absence, documented in §3)* |
| 18 | "sin interfaz" | No `frontend/`, no `index.html`, no `.jsx`/`.tsx`/`.js`/`.vue`/`.svelte` files, no CLI `argparse` entry point. §7 and §9 document this explicitly. | *(file absence, documented in §7/§9)* |
| 19 | "como dependencia en otros [proyectos]" | PEP 621 `pyproject.toml` with `py-modules = ["roman"]`, `package-dir = {"" = "src"}`, `requires-python = ">=3.9"`; installable via `pip install .` or `pip install -e .[dev]`, after which `from roman import to_roman` works in consuming projects. | `pyproject.toml`, `README.md` |
| 20 | Type hints on the public surface | Both public functions carry full annotations (`int -> str`, `str -> int`); module constants annotated (`MIN_VALUE: int`, `MAX_VALUE: int`, `NUMERAL_TABLE: List[Tuple[int, str]]`, `VALID_NUMERAL_CHARS: str`). No `Any`. | `src/roman.py` |
| 21 | Deterministic, testable error messages | Every `raise` uses the exact f-string templates in §2.3 so tests can assert with `pytest.raises(ValueError, match="not a canonical Roman numeral")`. | `src/roman.py`, `tests/test_roman.py` |
| 22 | Purity / thread-safety for a library dependency | No mutable module-level state, no I/O, no caching, no global counters; `NUMERAL_TABLE` is only read. Safe to import and call from any consumer context. | `src/roman.py` |

### 10.1 Required test cases in `tests/test_roman.py`

The following test functions MUST exist with these exact names:

| Test function | Assertion |
|---|---|
| `test_to_roman_known_values` | Parametrized: `1→"I"`, `2→"II"`, `3→"III"`, `4→"IV"`, `5→"V"`, `6→"VI"`, `9→"IX"`, `10→"X"`, `14→"XIV"`, `40→"XL"`, `44→"XLIV"`, `50→"L"`, `90→"XC"`, `100→"C"`, `400→"CD"`, `500→"D"`, `900→"CM"`, `1000→"M"`, `1990→"MCMXC"`, `2024→"MMXXIV"`. |
| `test_to_roman_bounds` | `to_roman(MIN_VALUE) == "I"`, `to_roman(MAX_VALUE) == "MMMCMXCIX"`. |
| `test_to_roman_out_of_range_raises_value_error` | Parametrized: `0`, `-1`, `-3999`, `4000`, `10000` → `pytest.raises(ValueError, match="expects 1 <= n <= 3999")`. |
| `test_to_roman_non_int_raises_type_error` | Parametrized: `1.0`, `"1"`, `None`, `[1]`, `(1,)`, `3+0j` → `pytest.raises(TypeError, match="expects int")`. |
| `test_to_roman_bool_raises_type_error` | `to_roman(True)` and `to_roman(False)` → `pytest.raises(TypeError, match="expects int, got bool")`. Explicitly guards the bool-subclasses-int trap. |
| `test_from_roman_known_values` | Parametrized inverse of the known-values table; includes `"IV"→4`, `"MCMXC"→1990`, `"MMMCMXCIX"→3999`. |
| `test_from_roman_accepts_lowercase_and_mixed_case` | `"mcmxc"→1990`, `"MmCmXc"→1990`, `"iv"→4`, `"mmmcmxcix"→3999`. |
| `test_from_roman_empty_string_raises_value_error` | `""` → `pytest.raises(ValueError, match="non-empty")`. |
| `test_from_roman_non_canonical_raises_value_error` | Parametrized: `"IIII"`, `"VV"`, `"IC"`, `"MMMM"`, `"XXXX"`, `"LC"`, `"DM"`, `"IL"`, `"VX"`, `"IIX"`, `"CCCC"`, `"DD"`, `"LL"` → `pytest.raises(ValueError, match="not a canonical Roman numeral")`. The four strings named in the goal (`IIII`, `VV`, `IC`, `MMMM`) MUST be present. |
| `test_from_roman_invalid_characters_raise_value_error` | `"ABC"`, `"XII3"`, `"X I"`, `"roman"` → `pytest.raises(ValueError)`. |
| `test_from_roman_non_str_raises_type_error` | `None`, `4`, `b"IV"`, `["I"]` → `pytest.raises(TypeError, match="expects str")`. |
| `test_roundtrip_all_values_1_to_3999` | Loop over `range(1, 4000)`: assert `isinstance(to_roman(n), str)`, `from_roman(to_roman(n)) == n`, `to_roman(from_roman(to_roman(n))) == to_roman(n)`, and `from_roman(to_roman(n).lower()) == n`. |
| `test_canonical_regex_conformance` | Loop over `1..3999`: result matches `^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$` (regex defined locally inside the test module — **not** in `src/roman.py`, which must stay regex-free). |

### 10.2 Constraint disclosure

No requirement in the goal depends on an unavailable external service, so no capability is faked. The library is fully implementable with the Python standard library alone, and nothing in these files will be a mock or placeholder.

---

## 11. ACCEPTANCE CRITERIA

The deliverable is accepted when all of the following hold:

1. `python -m pytest` run from the repository root passes with **0 failures, 0 errors, 0 skips**.
2. The roundtrip test executes all 3999 values and passes.
3. `to_roman(True)` raises `TypeError` (not `ValueError`, not a silent `"I"`).
4. `to_roman(0)`, `to_roman(-1)`, and `to_roman(4000)` each raise `ValueError`.
5. `from_roman("")` raises `ValueError`; `from_roman("IIII")`, `from_roman("VV")`, `from_roman("IC")`, and `from_roman("MMMM")` each raise `ValueError`.
6. `from_roman("mcmxc") == 1990`.
7. `src/roman.py` imports nothing outside the standard library, and `pip install .` succeeds with zero downloaded runtime dependencies.
8. `README.md` exists and documents both functions, the accepted range, and the error behavior.
9. No server, frontend, Docker, database, or environment-variable file exists in the repository.
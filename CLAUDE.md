# CLAUDE.md

## Project

ibkr2modelo720 — converts IBKR CSV portfolio exports into Modelo 720 files
for Spain's AEAT. TUI built with Textual.

## Language policy

- **Communication with the user**: always in Russian.
- **Application UI** (labels, messages, button text): always in English.
- **Code comments and docstrings**: always in English.

## Import style

Avoid importing symbols from modules. Import the module itself and use qualified names.

```python
# Good
import pathlib
import dataclasses as dcs
import decimal

path = pathlib.Path("file.txt")

@dcs.dataclass
class Foo:
    value: decimal.Decimal

# Bad
from pathlib import Path
from dataclasses import dataclass
from decimal import Decimal
```

Common aliases are fine when the module name is long:
- `import dataclasses as dcs`
- `import collections.abc as cabc`

## Running

```bash
uv run python -m ibkr2modelo720   # launch TUI
uv run pytest tests/ -v           # run tests
```

## Key architecture notes

- `modelo720.py` — core record generation (Tipo 1 and Tipo 2), 500 chars/line
- `csv_parser.py` — IBKR CSV parsing, merges duplicate ISINs
- `ecb_rates.py` — EUR/USD rate from ECB Statistical Data Warehouse API
- `writer.py` — writes ISO-8859-1 file with CRLF endings
- `screens/` — Textual screens: main form, preview table, result summary

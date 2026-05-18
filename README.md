# Python Compiler IDE

A browser-based Python compiler that demonstrates all four classical compiler phases — Lexical Analysis, Syntax Analysis, Semantic Analysis, and Symbol Table — built with Flask and a modern glass-morphism UI.

**Group Members:** Farah · Mahnoor · Zaynab

---

## Live Demo

> [View on Vercel](https://your-project.vercel.app) — _update link after deployment_

---

## What It Does

Write any Python code in the browser editor and run it through four compiler phases:

| Phase | Page | What you see |
|-------|------|-------------|
| **Lexer** | `/lexer-page` | Full token stream with type badges and line numbers |
| **Parser** | `/parser-page` | Pass/fail status + all recursive-descent parse steps |
| **Semantic** | `/semantic-page` | Errors (undefined variables) and warnings (redefined functions) |
| **Symbol Table** | `/symbol-page` | Every identifier — name, kind, type, scope, value, memory address |

Use the **Home page** to run all 4 phases at once with tabbed results.

---

## Screenshots

| Home — Run All | Symbol Table Page |
|---|---|
| _(add screenshot)_ | _(add screenshot)_ |

---

## Project Structure

```
compiler_project/
├── app.py                   Flask entry point + REST API
├── requirements.txt
├── vercel.json              Vercel deployment config
│
├── lexer/
│   └── lexer.py             Regex tokenizer with INDENT/DEDENT generation
├── parser/
│   └── parser.py            Recursive-descent parser for Python grammar
├── semantic/
│   └── semantic.py          Scope tracker and error detector
├── symbol_table/
│   └── symbol_table.py      Identifier registry with inferred types
│
└── templates/
    ├── base.html            Shared layout, sidebar, CSS, shared JS
    ├── index.html           Home page — Run All with tabbed results
    ├── lexer.html           Phase 1 dedicated page
    ├── parser.html          Phase 2 dedicated page
    ├── semantic.html        Phase 3 dedicated page
    └── symbol_table.html    Phase 4 dedicated page
```

---

## Run Locally

**Python 3.9+ required**

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/compiler_project.git
cd compiler_project

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
python app.py

# 4. Open browser
# http://127.0.0.1:5000
```

---

## API Reference

All endpoints accept `POST` with `Content-Type: application/json`.

**Request body:** `{ "code": "<python source code>" }`

| Endpoint | Returns |
|----------|---------|
| `POST /api/lexer` | `{ tokens, errors, log }` |
| `POST /api/parser` | `{ success, errors, parse_steps }` |
| `POST /api/semantic` | `{ success, errors, warnings, log }` |
| `POST /api/symbol_table` | `{ entries, log, summary }` |
| `POST /api/analyze_all` | All four results combined |

**Example — call the lexer:**
```bash
curl -X POST http://127.0.0.1:5000/api/lexer \
  -H "Content-Type: application/json" \
  -d '{"code": "x = 10\nprint(x)"}'
```

---

## Deploy to Vercel

**Option 1 — Vercel CLI**
```bash
npm install -g vercel
vercel
```
Follow the prompts. Your app goes live at a `*.vercel.app` URL.

**Option 2 — GitHub Auto-Deploy**
1. Push this repo to GitHub
2. Go to [vercel.com](https://vercel.com) → New Project → Import your repo
3. Vercel detects `vercel.json` automatically and deploys

Every future `git push` to `main` triggers a redeploy.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Frontend | Vanilla JS, HTML5, CSS3 (glass-morphism) |
| Fonts | Inter, JetBrains Mono |
| Icons | Font Awesome 6 |
| Hosting | Vercel |

---

## Compiler Phases — Technical Detail

### Lexer (`lexer/lexer.py`)
- Regex-based tokenizer using Python `re` named groups
- Token types: `KEYWORD`, `BUILTIN`, `IDENTIFIER`, `INTEGER`, `FLOAT`, `STRING`, `OPERATOR`, `OP_AUG`, `SEPARATOR`, `COMMENT`, `INDENT`, `DEDENT`, `NEWLINE`
- Generates INDENT/DEDENT tokens by tracking indentation stack — this is what makes it a real Python lexer
- Reports line numbers for every token and every error

### Parser (`parser/parser.py`)
- Recursive-descent (top-down) parser
- Handles: assignments, if/elif/else, for-in, while, def with parameters and return type annotation (`->`), class
- Full expression hierarchy: `or → and → not → comparison → arithmetic → term → factor → power → atom`
- Handles attribute access (`a.b`), subscript (`a[i]`), and function calls (`f(x, y)`) via `parse_atom_expr()`

### Semantic Analyzer (`semantic/semantic.py`)
- Tracks three scopes: `global_vars`, `local_vars`, `functions`
- Detects **use-before-assignment** for all identifiers
- Detects **duplicate function definitions** (warning, not error — Python allows this)
- Tracks `import` and `from … import` to whitelist module names
- Does NOT flag Python built-ins (`print`, `range`, `len`, etc.)

### Symbol Table (`symbol_table/symbol_table.py`)
- `SymbolTableEntry` stores: `name`, `kind`, `data_type`, `scope`, `value`, `address`
- `kind` values: `variable`, `function`, `class`, `parameter`, `module`
- Type inference from assigned literal: `int`, `float`, `str`, `bool`, `NoneType`, `unknown`
- Addresses are sequential hex values starting at `0x03E8`

---

## Sample Code to Test

```python
def factorial(n):
    result = 1
    for i in range(n):
        result = result * (i + 1)
    return result

count = 5
answer = factorial(count)
print(answer)
```

Paste this on the home page and click **Run All** to see all 4 phases at once.

---

*Built with Python, Flask, and vanilla JS.*

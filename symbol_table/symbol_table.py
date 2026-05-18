"""
Python Symbol Table Builder
============================
Air University — Compiler Construction Lab
Instructor: Ms. Rubab Hafeez

Builds a symbol table from a Python token list.
Tracks variables, functions, classes, and parameters
with inferred types, scope, and simulated addresses.
"""


def _infer_type(tok):
    """Infer a Python type name from an assigned-value token."""
    if tok is None:
        return 'unknown'
    tt, tv = tok['token_type'], tok['value']
    if tt == 'INTEGER':
        return 'int'
    if tt == 'FLOAT':
        return 'float'
    if tt == 'STRING':
        return 'str'
    if tt == 'KEYWORD' and tv in ('True', 'False'):
        return 'bool'
    if tt == 'KEYWORD' and tv == 'None':
        return 'NoneType'
    if tt in ('IDENTIFIER', 'BUILTIN') and tv in ('True', 'False'):
        return 'bool'
    if tt in ('IDENTIFIER', 'BUILTIN') and tv == 'None':
        return 'NoneType'
    return 'unknown'


class SymbolTableEntry:
    _address_counter = 1000

    def __init__(self, name, kind='variable', data_type='unknown', scope='global', value=None):
        self.name = name
        self.kind = kind           # 'variable' | 'function' | 'class' | 'parameter'
        self.data_type = data_type
        self.scope = scope
        self.value = value
        self.address = f"0x{SymbolTableEntry._address_counter:04X}"
        SymbolTableEntry._address_counter += 4

    def to_dict(self):
        return {
            'name': self.name,
            'kind': self.kind,
            'data_type': self.data_type,
            'scope': self.scope,
            'value': self.value if self.value is not None else '—',
            'address': self.address
        }


class SymbolTable:
    def __init__(self):
        self.table = []
        self.scope_stack = ['global']
        self.log = []
        SymbolTableEntry._address_counter = 1000

    def current_scope(self):
        return self.scope_stack[-1]

    def push_scope(self, name):
        self.scope_stack.append(name)

    def pop_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    def lookup(self, name):
        for e in self.table:
            if e.name == name:
                return e
        return None

    def add(self, name, kind='variable', data_type='unknown', value=None):
        existing = self.lookup(name)
        if existing:
            if value is not None and existing.value in (None, '—'):
                existing.value = value
            return existing
        entry = SymbolTableEntry(name, kind, data_type, self.current_scope(), value)
        self.table.append(entry)
        self.log.append(
            f"[SYMTABLE] Added {kind} '{name}' | type={data_type} | "
            f"scope={entry.scope} | addr={entry.address}"
        )
        return entry

    def build_from_tokens(self, token_list):
        self.table = []
        self.scope_stack = ['global']
        self.log = []
        SymbolTableEntry._address_counter = 1000

        self.log.append("[SYMTABLE] Building Python symbol table...")

        tokens = token_list
        n = len(tokens)
        i = 0
        in_function = False
        func_indent_start = -1
        indent_depth = 0

        while i < n:
            t = tokens[i]
            tt, tv = t['token_type'], t['value']

            if tt == 'INDENT':
                indent_depth += 1
                i += 1
                continue

            if tt == 'DEDENT':
                indent_depth -= 1
                if in_function and indent_depth <= func_indent_start:
                    self.pop_scope()
                    in_function = False
                    func_indent_start = -1
                i += 1
                continue

            # Function definition
            if tt == 'KEYWORD' and tv == 'def':
                if i + 1 < n and tokens[i + 1]['token_type'] == 'IDENTIFIER':
                    fname = tokens[i + 1]['value']
                    self.add(fname, 'function', 'function')
                    self.push_scope(fname)
                    in_function = True
                    func_indent_start = indent_depth
                    # Parse parameters inside parentheses
                    j = i + 2
                    paren = 0
                    while j < n:
                        pt = tokens[j]
                        if pt['value'] == '(':
                            paren += 1
                        elif pt['value'] == ')':
                            paren -= 1
                            if paren == 0:
                                break
                        elif pt['token_type'] == 'IDENTIFIER' and paren > 0:
                            prev = tokens[j - 1] if j > 0 else None
                            if prev and prev['value'] in ('(', ',', '*', '**'):
                                if pt['value'] != 'self':
                                    self.add(pt['value'], 'parameter', 'unknown')
                        j += 1
                i += 1
                continue

            # Class definition
            if tt == 'KEYWORD' and tv == 'class':
                if i + 1 < n and tokens[i + 1]['token_type'] == 'IDENTIFIER':
                    self.add(tokens[i + 1]['value'], 'class', 'class')
                i += 1
                continue

            # Import
            if tt == 'KEYWORD' and tv == 'import':
                if i + 1 < n and tokens[i + 1]['token_type'] in ('IDENTIFIER', 'BUILTIN'):
                    self.add(tokens[i + 1]['value'], 'variable', 'module')
                i += 1
                continue

            if tt == 'KEYWORD' and tv == 'from':
                j = i + 1
                while j < n and tokens[j]['value'] != 'import':
                    j += 1
                if j + 1 < n and tokens[j + 1]['token_type'] in ('IDENTIFIER', 'BUILTIN'):
                    self.add(tokens[j + 1]['value'], 'variable', 'module')
                i += 1
                continue

            # For loop variable
            if tt == 'KEYWORD' and tv == 'for':
                if i + 1 < n and tokens[i + 1]['token_type'] == 'IDENTIFIER':
                    self.add(tokens[i + 1]['value'], 'variable', 'unknown')
                i += 1
                continue

            # Assignment: IDENTIFIER = value
            if tt == 'IDENTIFIER':
                nxt = tokens[i + 1] if i + 1 < n else None
                if nxt and nxt['token_type'] == 'OPERATOR' and nxt['value'] == '=':
                    val_tok = tokens[i + 2] if i + 2 < n else None
                    inferred = _infer_type(val_tok)
                    val = (val_tok['value']
                           if val_tok and val_tok['token_type'] in ('INTEGER', 'FLOAT', 'STRING', 'KEYWORD')
                           else None)
                    self.add(tv, 'variable', inferred, val)

            i += 1

        self.log.append(f"[SYMTABLE] Done. {len(self.table)} symbol(s) found.")

    def get_results(self):
        return {
            'entries': [e.to_dict() for e in self.table],
            'log': self.log,
            'summary': {'total_symbols': len(self.table)}
        }

    def display(self):
        print(f"{'Name':<15} {'Kind':<12} {'Type':<10} {'Scope':<12} {'Value':<12} {'Address'}")
        print("-" * 75)
        for e in self.table:
            val = str(e.value) if e.value else '—'
            print(f"{e.name:<15} {e.kind:<12} {e.data_type:<10} {e.scope:<12} {val:<12} {e.address}")

"""
Python Lexical Analyzer
=======================
Air University — Compiler Construction Lab
Instructor: Ms. Rubab Hafeez

Tokenizes Python source code using regex patterns.
Generates INDENT/DEDENT tokens for block structure (PEP 8).
"""

import re

PYTHON_KEYWORDS = frozenset({
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
    'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
    'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
    'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
    'while', 'with', 'yield'
})

BUILTIN_NAMES = frozenset({
    'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple',
    'range', 'print', 'len', 'input', 'type', 'abs', 'max', 'min',
    'sum', 'sorted', 'reversed', 'enumerate', 'zip', 'map', 'filter',
    'hasattr', 'getattr', 'setattr', 'isinstance', 'issubclass', 'super',
    'repr', 'format', 'id', 'hex', 'oct', 'bin', 'chr', 'ord', 'round',
    'pow', 'open', 'any', 'all', 'object', 'Exception', 'ValueError',
    'TypeError', 'KeyError', 'IndexError', 'AttributeError', 'RuntimeError',
})

TOKEN_PATTERNS = [
    ('COMMENT',    r'#[^\n]*'),
    ('STRING',     r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|f"[^"\n]*"|f\'[^\'\n]*\'|"[^"\n]*"|\'[^\'\n]*\''),
    ('FLOAT',      r'\b\d+\.\d+([eE][+\-]?\d+)?\b|\b\d+[eE][+\-]?\d+\b'),
    ('INTEGER',    r'\b\d+\b'),
    ('OP_AUG',     r'\*\*=|//=|[+\-*/%&|^]='),
    ('OPERATOR',   r'\*\*|//|==|!=|<=|>=|->|:=|[+\-*/%=<>&|^~@]'),
    ('SEPARATOR',  r'[;,:()\[\]{}.]'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('WHITESPACE', r'[ \t]+'),
    ('MISMATCH',   r'.'),
]

MASTER_REGEX = '|'.join(f'(?P<{n}>{p})' for n, p in TOKEN_PATTERNS)


class Token:
    def __init__(self, token_type, value, line):
        self.token_type = token_type
        self.value = value
        self.line = line

    def to_dict(self):
        return {'token_type': self.token_type, 'value': self.value, 'line': self.line}

    def __repr__(self):
        return f"Token({self.token_type}, '{self.value}', line={self.line})"


class LexerError:
    def __init__(self, message, line):
        self.message = message
        self.line = line

    def to_dict(self):
        return {'message': self.message, 'line': self.line}


class Lexer:
    """
    Python lexical analyzer.
    Handles indentation by generating INDENT/DEDENT tokens,
    matching the behavior described in the Python Language Reference.
    """

    def __init__(self):
        self.tokens = []
        self.errors = []
        self.log = []

    def tokenize(self, source_code):
        self.tokens = []
        self.errors = []
        self.log = []

        self.log.append("[LEXER] Starting Python lexical analysis...")

        lines = source_code.split('\n')
        indent_stack = [0]
        line_number = 0

        for raw_line in lines:
            line_number += 1
            stripped = raw_line.lstrip(' \t')

            # Skip blank lines and comment-only lines for indentation purposes
            if not stripped or stripped.startswith('#'):
                continue

            indent = len(raw_line) - len(stripped)

            # Generate INDENT / DEDENT tokens based on indentation level
            if indent > indent_stack[-1]:
                indent_stack.append(indent)
                self.tokens.append(Token('INDENT', '<INDENT>', line_number))
                self.log.append(f"[LEXER] INDENT at line {line_number} (level={indent})")
            elif indent < indent_stack[-1]:
                while len(indent_stack) > 1 and indent < indent_stack[-1]:
                    indent_stack.pop()
                    self.tokens.append(Token('DEDENT', '<DEDENT>', line_number))
                    self.log.append(f"[LEXER] DEDENT at line {line_number}")
                if indent_stack[-1] != indent:
                    err = LexerError("Unexpected indentation level", line_number)
                    self.errors.append(err)
                    self.log.append(f"[LEXER ERROR] Indentation error at line {line_number}")

            self._tokenize_line(raw_line, line_number)
            self.tokens.append(Token('NEWLINE', '\\n', line_number))

        # Close all remaining indentation levels
        while len(indent_stack) > 1:
            indent_stack.pop()
            self.tokens.append(Token('DEDENT', '<DEDENT>', line_number))

        self.log.append(f"[LEXER] Done. Tokens: {len(self.tokens)}, Errors: {len(self.errors)}")
        return self.tokens, self.errors

    def _tokenize_line(self, line, line_number):
        for match in re.finditer(MASTER_REGEX, line):
            kind = match.lastgroup
            value = match.group()

            if kind == 'WHITESPACE':
                continue
            if kind == 'COMMENT':
                self.log.append(f"[LEXER] Skipped comment at line {line_number}")
                break
            if kind == 'MISMATCH':
                err = LexerError(f"Unexpected character '{value}'", line_number)
                self.errors.append(err)
                self.log.append(f"[LEXER ERROR] {err.message} at line {line_number}")
                continue

            if kind == 'IDENTIFIER':
                if value in PYTHON_KEYWORDS:
                    kind = 'KEYWORD'
                elif value in BUILTIN_NAMES:
                    kind = 'BUILTIN'

            tok = Token(kind, value, line_number)
            self.tokens.append(tok)
            self.log.append(f"[LEXER] Token: {kind:12s} | '{value}' | line {line_number}")

    def get_results(self):
        # Filter structural tokens (INDENT/DEDENT/NEWLINE) from display
        STRUCTURAL = frozenset(('INDENT', 'DEDENT', 'NEWLINE'))
        display = [t for t in self.tokens if t.token_type not in STRUCTURAL]
        return {
            'tokens': [t.to_dict() for t in display],
            'errors': [e.to_dict() for e in self.errors],
            'log': self.log,
            'summary': {
                'total_tokens': len(display),
                'total_errors': len(self.errors)
            }
        }

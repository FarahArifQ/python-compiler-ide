"""
Python Syntax Analyzer (Parser)
================================
Recursive-descent parser for a Python subset.
Uses INDENT/DEDENT tokens from the lexer for block structure.

Supported grammar:
  program      → stmt_list
  stmt_list    → (NEWLINE | stmt)*
  stmt         → simple_stmt | compound_stmt
  compound     → if_stmt | while_stmt | for_stmt | funcdef | classdef
  simple       → assign | aug_assign | expr_stmt | return | pass | break | continue | import
  suite        → ':' NEWLINE INDENT stmt_list DEDENT
  if_stmt      → 'if' expr suite ('elif' expr suite)* ('else' suite)?
  while_stmt   → 'while' expr suite
  for_stmt     → 'for' IDENTIFIER 'in' expr suite
  funcdef      → 'def' IDENTIFIER '(' params ')' suite
  assign       → IDENTIFIER '=' expr NEWLINE
  aug_assign   → IDENTIFIER OP_AUG expr NEWLINE
  expr_stmt    → expr NEWLINE
"""


class ParseError:
    def __init__(self, message, line):
        self.message = message
        self.line = line

    def to_dict(self):
        return {'message': self.message, 'line': self.line}


class Parser:
    def __init__(self):
        self.tokens = []
        self.pos = 0
        self.errors = []
        self.log = []
        self.parse_steps = []

    # ------------------------------------------------------------------
    # Token helpers
    # ------------------------------------------------------------------

    def tok(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def peek_type(self):
        t = self.tok()
        return t['token_type'] if t else None

    def peek_value(self):
        t = self.tok()
        return t['value'] if t else None

    def peek_line(self):
        t = self.tok()
        return t['line'] if t else '?'

    def consume(self):
        t = self.tok()
        self.pos += 1
        return t

    def expect(self, value=None, token_type=None):
        t = self.tok()
        if t is None:
            self._error(f"Unexpected end of input (expected '{value or token_type}')", '?')
            return None
        if value is not None and t['value'] != value:
            self._error(f"Expected '{value}' but found '{t['value']}'", t['line'])
            return None
        if token_type is not None and t['token_type'] != token_type:
            self._error(f"Expected {token_type} but found '{t['value']}'", t['line'])
            return None
        return self.consume()

    def expect_type(self, token_type):
        t = self.tok()
        if t is None:
            self._error(f"Expected {token_type} but reached end of input", '?')
            return None
        if t['token_type'] != token_type:
            self._error(f"Expected {token_type} but found '{t['value']}' ({t['token_type']})", t['line'])
            return None
        return self.consume()

    def skip_newlines(self):
        while self.peek_type() == 'NEWLINE':
            self.consume()

    def _error(self, msg, line):
        self.errors.append(ParseError(msg, line))
        self.log.append(f"[PARSER ERROR] {msg} at line {line}")

    def _step(self, msg):
        self.parse_steps.append(msg)
        self.log.append(f"[PARSER] {msg}")

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def parse(self, token_list):
        self.tokens = token_list
        self.pos = 0
        self.errors = []
        self.log = []
        self.parse_steps = []

        self.log.append("[PARSER] Starting Python syntax analysis...")
        self._step("Parsing Python program...")

        self.parse_stmt_list()

        # Any remaining non-whitespace tokens are unexpected
        while self.tok() and self.peek_type() not in ('NEWLINE', 'DEDENT'):
            t = self.tok()
            self._error(f"Unexpected token '{t['value']}' after program end", t['line'])
            self.consume()

        if not self.errors:
            self.log.append("[PARSER] Syntax analysis PASSED — no errors found.")
        else:
            self.log.append(f"[PARSER] Syntax analysis FAILED — {len(self.errors)} error(s).")

        return len(self.errors) == 0

    # ------------------------------------------------------------------
    # Statement list
    # ------------------------------------------------------------------

    def parse_stmt_list(self):
        self.skip_newlines()
        while self.tok() and self.peek_type() not in ('DEDENT',):
            self.parse_stmt()
            self.skip_newlines()

    def parse_stmt(self):
        t = self.tok()
        if t is None:
            return

        tt, tv = t['token_type'], t['value']

        # Compound statements
        if tt == 'KEYWORD':
            if tv == 'if':       self.parse_if_stmt();     return
            if tv == 'while':    self.parse_while_stmt();  return
            if tv == 'for':      self.parse_for_stmt();    return
            if tv == 'def':      self.parse_funcdef();     return
            if tv == 'class':    self.parse_classdef();    return
            if tv == 'return':   self.parse_return_stmt(); return
            if tv in ('import', 'from'): self.parse_import_stmt(); return
            if tv == 'pass':
                self._step(f"pass at line {t['line']}")
                self.consume(); self.skip_newlines(); return
            if tv == 'break':
                self._step(f"break at line {t['line']}")
                self.consume(); self.skip_newlines(); return
            if tv == 'continue':
                self._step(f"continue at line {t['line']}")
                self.consume(); self.skip_newlines(); return
            # 'not', 'True', 'False', 'None' can start expressions
            self.parse_expr_stmt()
            return

        if tt in ('IDENTIFIER', 'BUILTIN'):
            # Lookahead: assignment vs expression statement
            nxt = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if nxt:
                if nxt['token_type'] == 'OPERATOR' and nxt['value'] == '=':
                    self.parse_assign_stmt(); return
                if nxt['token_type'] == 'OP_AUG':
                    self.parse_aug_assign_stmt(); return
            self.parse_expr_stmt()
            return

        # Literals / other expression starters
        self.parse_expr_stmt()

    # ------------------------------------------------------------------
    # Simple statements
    # ------------------------------------------------------------------

    def parse_assign_stmt(self):
        id_tok = self.consume()
        self._step(f"Assignment '{id_tok['value']}' at line {id_tok['line']}")
        self.expect('=')
        self.parse_expr()
        self.skip_newlines()
        self._step(f"  → {id_tok['value']} = expr  [Assign]")

    def parse_aug_assign_stmt(self):
        id_tok = self.consume()
        op_tok = self.consume()
        self._step(f"Augmented assign '{id_tok['value']} {op_tok['value']}' at line {id_tok['line']}")
        self.parse_expr()
        self.skip_newlines()
        self._step(f"  → {id_tok['value']} {op_tok['value']} expr  [AugAssign]")

    def parse_expr_stmt(self):
        self._step(f"Expression statement at line {self.peek_line()}")
        self.parse_expr()
        self.skip_newlines()

    def parse_return_stmt(self):
        kw = self.consume()
        self._step(f"return at line {kw['line']}")
        if self.peek_type() not in ('NEWLINE', 'DEDENT') and self.tok() is not None:
            self.parse_expr()
        self.skip_newlines()

    def parse_import_stmt(self):
        kw = self.consume()
        self._step(f"import at line {kw['line']}")
        if self.peek_type() in ('IDENTIFIER', 'BUILTIN'):
            mod = self.consume()
            self._step(f"  → import '{mod['value']}'")
        if kw['value'] == 'from' and self.peek_value() == 'import':
            self.consume()
            if self.peek_type() in ('IDENTIFIER', 'BUILTIN'):
                name = self.consume()
                self._step(f"  → from ... import '{name['value']}'")
        self.skip_newlines()

    # ------------------------------------------------------------------
    # Compound statements
    # ------------------------------------------------------------------

    def parse_suite(self):
        """Parses: ':' NEWLINE INDENT stmt_list DEDENT"""
        self.expect(':')
        self.skip_newlines()
        if self.peek_type() != 'INDENT':
            self._error("Expected indented block after ':'", self.peek_line())
            return
        self.consume()  # INDENT
        self.parse_stmt_list()
        if self.peek_type() == 'DEDENT':
            self.consume()  # DEDENT

    def parse_if_stmt(self):
        self._step(f"if at line {self.peek_line()}")
        self.consume()  # 'if'
        self.parse_expr()
        self.parse_suite()
        self._step("  → if-block parsed")

        while self.peek_value() == 'elif':
            self._step(f"elif at line {self.peek_line()}")
            self.consume()
            self.parse_expr()
            self.parse_suite()
            self._step("  → elif-block parsed")

        if self.peek_value() == 'else':
            self._step(f"else at line {self.peek_line()}")
            self.consume()
            self.parse_suite()
            self._step("  → else-block parsed")

    def parse_while_stmt(self):
        self._step(f"while at line {self.peek_line()}")
        self.consume()  # 'while'
        self.parse_expr()
        self.parse_suite()
        self._step("  → while-body parsed")

    def parse_for_stmt(self):
        self._step(f"for at line {self.peek_line()}")
        self.consume()  # 'for'
        if self.peek_type() in ('IDENTIFIER', 'BUILTIN'):
            var = self.consume()
            self._step(f"  loop variable: '{var['value']}'")
        if self.peek_value() == 'in':
            self.consume()
        else:
            self._error("Expected 'in' keyword in for statement", self.peek_line())
        self.parse_expr()
        self.parse_suite()
        self._step("  → for-body parsed")

    def parse_funcdef(self):
        self._step(f"def at line {self.peek_line()}")
        self.consume()  # 'def'
        name = self.expect_type('IDENTIFIER')
        fname = name['value'] if name else '?'
        self.expect('(')
        params = self.parse_params()
        self.expect(')')
        if self.peek_value() == '->':  # return type annotation
            self.consume()
            self.parse_expr()
        self.parse_suite()
        self._step(f"  → def {fname}({', '.join(params)}) parsed")

    def parse_params(self):
        params = []
        while self.peek_type() in ('IDENTIFIER', 'BUILTIN') or self.peek_value() in ('*', '**'):
            if self.peek_value() in ('*', '**'):
                self.consume()
            t = self.tok()
            if t and t['token_type'] in ('IDENTIFIER', 'BUILTIN'):
                params.append(t['value'])
                self.consume()
                if self.peek_value() == '=':  # default value
                    self.consume()
                    self.parse_expr()
                if self.peek_value() == ':':  # type annotation
                    self.consume()
                    self.parse_expr()
            if self.peek_value() != ',':
                break
            self.consume()  # ','
        return params

    def parse_classdef(self):
        self._step(f"class at line {self.peek_line()}")
        self.consume()  # 'class'
        name = self.expect_type('IDENTIFIER')
        if self.peek_value() == '(':
            self.consume()
            while self.peek_value() != ')' and self.tok():
                self.consume()
            self.expect(')')
        self.parse_suite()
        self._step(f"  → class '{name['value'] if name else '?'}' parsed")

    # ------------------------------------------------------------------
    # Expressions  (Pratt-style precedence ladder)
    # ------------------------------------------------------------------

    def parse_expr(self):
        self.parse_or_expr()

    def parse_or_expr(self):
        self.parse_and_expr()
        while self.peek_value() == 'or':
            self.consume()
            self.parse_and_expr()

    def parse_and_expr(self):
        self.parse_not_expr()
        while self.peek_value() == 'and':
            self.consume()
            self.parse_not_expr()

    def parse_not_expr(self):
        if self.peek_value() == 'not':
            self.consume()
            self.parse_not_expr()
        else:
            self.parse_comparison()

    def parse_comparison(self):
        self.parse_arith()
        CMP_OPS = frozenset({'<', '>', '==', '!=', '<=', '>='})
        while True:
            v = self.peek_value()
            if v in CMP_OPS:
                self.consume()
                self.parse_arith()
            elif self.peek_type() == 'KEYWORD' and v == 'in':
                self.consume()
                self.parse_arith()
            elif self.peek_type() == 'KEYWORD' and v == 'not':
                # 'not in'
                self.consume()
                if self.peek_value() == 'in':
                    self.consume()
                    self.parse_arith()
            elif self.peek_type() == 'KEYWORD' and v == 'is':
                self.consume()
                if self.peek_value() == 'not':
                    self.consume()
                self.parse_arith()
            else:
                break

    def parse_arith(self):
        self.parse_term()
        while self.peek_value() in ('+', '-'):
            self.consume()
            self.parse_term()

    def parse_term(self):
        self.parse_factor()
        while self.peek_value() in ('*', '/', '//', '%', '@'):
            self.consume()
            self.parse_factor()

    def parse_factor(self):
        if self.peek_value() in ('-', '+', '~'):
            self.consume()
            self.parse_factor()
        else:
            self.parse_power()

    def parse_power(self):
        self.parse_atom_expr()
        if self.peek_value() == '**':
            self.consume()
            self.parse_factor()

    def parse_atom_expr(self):
        self.parse_atom()
        while True:
            if self.peek_value() == '.':
                self.consume()
                if self.peek_type() in ('IDENTIFIER', 'BUILTIN', 'KEYWORD'):
                    self.consume()
            elif self.peek_value() == '[':
                self.consume()
                self.parse_expr()
                self.expect(']')
            elif self.peek_value() == '(':
                self.consume()
                self.parse_arglist()
                self.expect(')')
            else:
                break

    def parse_atom(self):
        t = self.tok()
        if t is None:
            self._error("Expected expression but reached end of input", '?')
            return

        tt, tv = t['token_type'], t['value']

        if tt in ('INTEGER', 'FLOAT', 'STRING'):
            self.consume()
        elif tt in ('IDENTIFIER', 'BUILTIN'):
            self.consume()
        elif tt == 'KEYWORD' and tv in ('True', 'False', 'None'):
            self.consume()
        elif tv == '(':
            self.consume()
            if self.peek_value() != ')':
                self.parse_expr()
                while self.peek_value() == ',':
                    self.consume()
                    if self.peek_value() != ')':
                        self.parse_expr()
            self.expect(')')
        elif tv == '[':
            self.consume()
            if self.peek_value() != ']':
                self.parse_expr()
                while self.peek_value() == ',':
                    self.consume()
                    if self.peek_value() != ']':
                        self.parse_expr()
            self.expect(']')
        elif tv == '{':
            self.consume()
            if self.peek_value() != '}':
                self.parse_expr()
                if self.peek_value() == ':':
                    self.consume()
                    self.parse_expr()
                while self.peek_value() == ',':
                    self.consume()
                    if self.peek_value() != '}':
                        self.parse_expr()
                        if self.peek_value() == ':':
                            self.consume()
                            self.parse_expr()
            self.expect('}')
        else:
            self._error(f"Unexpected token '{tv}' in expression", t['line'])
            self.consume()

    def parse_arglist(self):
        if self.peek_value() == ')':
            return
        # Handle keyword argument: name=value
        nxt = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
        if self.peek_type() in ('IDENTIFIER', 'BUILTIN') and nxt and nxt['value'] == '=':
            self.consume(); self.consume()
        self.parse_expr()
        while self.peek_value() == ',':
            self.consume()
            if self.peek_value() in (')', None):
                break
            nxt2 = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if self.peek_type() in ('IDENTIFIER', 'BUILTIN') and nxt2 and nxt2['value'] == '=':
                self.consume(); self.consume()
            if self.peek_value() not in (')', None):
                self.parse_expr()

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def get_results(self):
        return {
            'success': len(self.errors) == 0,
            'errors': [e.to_dict() for e in self.errors],
            'parse_steps': self.parse_steps,
            'log': self.log,
            'summary': {
                'total_errors': len(self.errors),
                'status': 'PASSED' if not self.errors else 'FAILED'
            }
        }

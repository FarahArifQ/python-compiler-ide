"""
Python Semantic Analyzer
========================
Performs semantic checks on Python token stream:
  1. Use before assignment (undefined variable)
  2. Duplicate function definitions
  3. Scope analysis (global vs local)
  4. Import statement tracking
"""

_BUILTINS = frozenset({
    'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple',
    'range', 'print', 'len', 'input', 'type', 'abs', 'max', 'min',
    'sum', 'sorted', 'reversed', 'enumerate', 'zip', 'map', 'filter',
    'hasattr', 'getattr', 'setattr', 'isinstance', 'issubclass', 'super',
    'repr', 'format', 'id', 'hex', 'oct', 'bin', 'chr', 'ord', 'round',
    'pow', 'open', 'any', 'all', 'object', 'self',
    'True', 'False', 'None',
    'Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError',
    'AttributeError', 'RuntimeError', 'StopIteration',
    '__name__', '__file__', '__doc__',
})

_KEYWORDS = frozenset({
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
    'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
    'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
    'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
    'while', 'with', 'yield'
})


class SemanticError:
    def __init__(self, message, line):
        self.message = message
        self.line = line

    def to_dict(self):
        return {'message': self.message, 'line': self.line}


class SemanticAnalyzer:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.log = []
        self.global_vars = set()
        self.local_vars = set()
        self.functions = set()
        self.in_function = False
        self.indent_depth = 0
        self.func_indent_start = -1

    def _error(self, msg, line):
        self.errors.append(SemanticError(msg, line))
        self.log.append(f"[SEMANTIC ERROR] {msg} at line {line}")

    def _warn(self, msg, line):
        self.warnings.append({'message': msg, 'line': line})
        self.log.append(f"[SEMANTIC WARNING] {msg} at line {line}")

    def _is_defined(self, name):
        return (name in self.global_vars or
                name in self.local_vars or
                name in self.functions or
                name in _BUILTINS or
                name in _KEYWORDS)

    def analyze(self, token_list):
        self.errors = []
        self.warnings = []
        self.log = []
        self.global_vars = set()
        self.local_vars = set()
        self.functions = set()
        self.in_function = False
        self.indent_depth = 0
        self.func_indent_start = -1

        self.log.append("[SEMANTIC] Starting Python semantic analysis...")

        tokens = token_list
        n = len(tokens)
        i = 0

        while i < n:
            t = tokens[i]
            tt, tv, ln = t['token_type'], t['value'], t['line']

            # Track block depth
            if tt == 'INDENT':
                self.indent_depth += 1
                i += 1
                continue

            if tt == 'DEDENT':
                self.indent_depth -= 1
                if self.in_function and self.indent_depth <= self.func_indent_start:
                    self.in_function = False
                    self.local_vars = set()
                    self.func_indent_start = -1
                    self.log.append("[SEMANTIC] Left function scope")
                i += 1
                continue

            # Function definition
            if tt == 'KEYWORD' and tv == 'def':
                if i + 1 < n and tokens[i + 1]['token_type'] == 'IDENTIFIER':
                    fname = tokens[i + 1]['value']
                    if fname in self.functions:
                        self._warn(f"Function '{fname}' is redefined", ln)
                    else:
                        self.functions.add(fname)
                        self.global_vars.add(fname)
                        self.log.append(f"[SEMANTIC] Function '{fname}' defined at line {ln}")
                    # Collect parameters: scan until ':'
                    j = i + 2
                    paren_depth = 0
                    while j < n:
                        pt = tokens[j]
                        if pt['value'] == '(':
                            paren_depth += 1
                        elif pt['value'] == ')':
                            paren_depth -= 1
                            if paren_depth == 0:
                                j += 1
                                break
                        elif pt['token_type'] == 'IDENTIFIER' and paren_depth > 0:
                            prev = tokens[j - 1] if j > 0 else None
                            if prev and prev['value'] in ('(', ',', '*', '**'):
                                self.local_vars.add(pt['value'])
                                self.log.append(f"[SEMANTIC] Parameter '{pt['value']}' in '{fname}'")
                        j += 1
                    self.in_function = True
                    self.func_indent_start = self.indent_depth
                i += 1
                continue

            # Class definition
            if tt == 'KEYWORD' and tv == 'class':
                if i + 1 < n and tokens[i + 1]['token_type'] == 'IDENTIFIER':
                    cname = tokens[i + 1]['value']
                    self.global_vars.add(cname)
                    self.log.append(f"[SEMANTIC] Class '{cname}' defined at line {ln}")
                i += 1
                continue

            # Import
            if tt == 'KEYWORD' and tv == 'import':
                if i + 1 < n and tokens[i + 1]['token_type'] in ('IDENTIFIER', 'BUILTIN'):
                    mod = tokens[i + 1]['value']
                    self.global_vars.add(mod)
                    self.log.append(f"[SEMANTIC] Imported module '{mod}' at line {ln}")
                i += 1
                continue

            if tt == 'KEYWORD' and tv == 'from':
                j = i + 1
                while j < n and tokens[j]['value'] != 'import':
                    j += 1
                if j + 1 < n and tokens[j + 1]['token_type'] in ('IDENTIFIER', 'BUILTIN'):
                    imported = tokens[j + 1]['value']
                    self.global_vars.add(imported)
                    self.log.append(f"[SEMANTIC] from-import '{imported}' at line {ln}")
                i += 1
                continue

            # For loop variable
            if tt == 'KEYWORD' and tv == 'for':
                if i + 1 < n and tokens[i + 1]['token_type'] == 'IDENTIFIER':
                    loop_var = tokens[i + 1]['value']
                    if self.in_function:
                        self.local_vars.add(loop_var)
                    else:
                        self.global_vars.add(loop_var)
                    self.log.append(f"[SEMANTIC] Loop variable '{loop_var}' at line {ln}")
                i += 1
                continue

            # Assignment: IDENTIFIER = ...
            if tt == 'IDENTIFIER':
                nxt = tokens[i + 1] if i + 1 < n else None

                if nxt and nxt['token_type'] == 'OPERATOR' and nxt['value'] == '=':
                    # This is an assignment — declare the variable
                    if self.in_function:
                        self.local_vars.add(tv)
                    else:
                        self.global_vars.add(tv)
                    self.log.append(f"[SEMANTIC] Variable '{tv}' assigned at line {ln}")
                    i += 1
                    continue

                if nxt and nxt['token_type'] == 'OP_AUG':
                    # Augmented assignment — must already exist
                    if not self._is_defined(tv):
                        self._error(f"Variable '{tv}' used before assignment", ln)
                    i += 1
                    continue

                # Variable usage — check it's been defined
                prev = tokens[i - 1] if i > 0 else None
                # Skip: attribute access, function/class/import names, 'as' targets
                if prev and prev['value'] in ('.', 'def', 'class', 'import', 'from', 'as', 'global', 'nonlocal'):
                    i += 1
                    continue

                if not self._is_defined(tv):
                    self._error(f"Variable '{tv}' used before assignment", ln)
                else:
                    self.log.append(f"[SEMANTIC] '{tv}' used at line {ln} ✓")

            i += 1

        if not self.errors:
            self.log.append("[SEMANTIC] No semantic errors found.")
        else:
            self.log.append(f"[SEMANTIC] {len(self.errors)} error(s) detected.")

        return len(self.errors) == 0

    def get_results(self):
        return {
            'success': len(self.errors) == 0,
            'errors': [e.to_dict() for e in self.errors],
            'warnings': self.warnings,
            'log': self.log,
            'summary': {
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings),
                'status': 'PASSED' if not self.errors else 'FAILED'
            }
        }

"""
Sample programs for testing the Mini Compiler IDE.
Each is a valid/invalid TINY-C program from lab exercises.
"""

EXAMPLES = {
    "basic_declarations": """\
// Basic variable declarations (Lab 3 style)
int x;
float y;
int a = 5;
float b = 3.14;
""",

    "tiny_c_program": """\
// TINY-C program from Lab 7
int a = 5;
int b = 10;
int c = 0;
c = a + b;
if (c > a) {
    print c;
} else {
    print a;
}
""",

    "arithmetic": """\
// Arithmetic expressions (Lab Task 09)
int x = 10;
int y = 20;
int result = 0;
result = x + y;
result = x * y;
result = result - x;
""",

    "while_loop": """\
// While loop example
int i = 0;
int sum = 0;
while (i < 10) {
    sum = sum + i;
    i = i + 1;
}
print sum;
""",

    "type_mismatch_error": """\
// Semantic error: type mismatch
int x = 3.14;
float y = 10;
""",

    "undeclared_error": """\
// Semantic error: undeclared variable
int a = 5;
b = a + 10;
""",

    "duplicate_error": """\
// Semantic error: duplicate declaration
int x = 5;
int x = 10;
""",

    "lexer_error": """\
// Lexical error: invalid character
int a = 5;
int b = 10@;
float c = 2.5;
"""
}

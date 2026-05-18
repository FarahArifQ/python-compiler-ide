# Example 1: Basic variable declarations and arithmetic (Lab 8 style)
EXAMPLE_1 = """\
int x = 5;
int y = 10;
float z = 3.14;
x = x + y;
y = x - 2;
"""

# Example 2: TINY C program with if-else (Lab 7 style)
EXAMPLE_2 = """\
int a = 5;
int b = 10;
int c = 0;
c = a + b;
if (c > a) {
    print c;
} else {
    print a;
}
"""

# Example 3: While loop
EXAMPLE_3 = """\
int i = 0;
int sum = 0;
while (i < 10) {
    sum = sum + i;
    i = i + 1;
}
"""

# Example 4: Program with semantic errors (undeclared variable, type mismatch)
EXAMPLE_4 = """\
int x = 5;
int x = 10;
y = x + 1;
"""

# Example 5: Division by zero
EXAMPLE_5 = """\
int a = 10;
int b = 0;
a = a / 0;
"""

ALL_EXAMPLES = {
    "Example 1: Basic Arithmetic": EXAMPLE_1,
    "Example 2: If-Else (TINY C)": EXAMPLE_2,
    "Example 3: While Loop":       EXAMPLE_3,
    "Example 4: Semantic Errors":  EXAMPLE_4,
    "Example 5: Division by Zero": EXAMPLE_5,
}

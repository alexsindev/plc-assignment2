# Statement Layer Notes

This branch adds the AST-backed statement layer for the project language.

## AST file layout

- `src/example/components/ast/expression.py`
  - expression nodes, `DataType`, arithmetic/comparison enums, and function signature metadata
- `src/example/components/ast/statement.py`
  - statement nodes and return-flow behavior

## Type model alignment

- Statement code now uses the same `DataType` enum as the merged expression layer.
- Variable bindings in `Memory` store those enum values, not raw strings.
- Function parameter and return signatures are tracked as enum-backed `FunctionType`.

## Implemented statement nodes

- `Statement_assignment`
  - Syntax: `name = expr;`
  - First assignment creates the variable in the current frame.
  - Reassignment in the same frame must keep the original type.

- `Statement_if`
  - Syntax: `if (condition) { ... } else { ... }`
  - The condition must evaluate to `bool`.
  - The `else` block is optional.

- `Statement_while`
  - Syntax: `while (condition) { ... }`
  - The condition must evaluate to `bool`.
  - The loop body runs until the condition becomes `false`.

- `Statement_print`
  - Syntax: `print(expr);`
  - Accepts `int`, `float`, `bool`, and `string`.
  - Printed values are appended to `Memory.output`.

- `Statement_block`
  - Syntax: `{ stmt1; stmt2; ... }`
  - A block stores a list of statements and runs them in order.
  - Blocks do not create a new variable frame by themselves.
  - Function calls create frames; plain `if`/`while` blocks do not.

- `Statement_function`
  - Syntax: `func name(param1, param2) { ... }`
  - Functions are registered in global scope.
  - Arguments are passed by value.
  - Parameter types are locked from the first successful call.
  - Return type is also locked from the first successful call.

- `Statement_return`
  - Syntax: `return expr;`
  - Returns from the innermost active function using a `ReturnSignal`.

## Expression support used by statements

- Arithmetic expressions: `+`, `-`, `*`, `/`
- Comparison expressions: `<`, `<=`, `>`, `>=`, `==`, `!=`
- Literals: `int`, `float`, `bool`, `string`
- Variables: `name`
- Function calls: `name(args...)`

## Static typing rules enforced in this branch

- Variable type is fixed by the first assignment in the current frame.
- Reassigning a variable to a different type raises `TypeError`.
- Arithmetic only accepts matching numeric types.
- Comparison only accepts matching numeric types and returns `bool`.
- `if` and `while` conditions must be `bool`.
- Function argument count must match the parameter count.
- Once a function is first called, later calls must use the same parameter types.
- Once a function returns a type, later returns from that function must match it.

## Static binding / scope behavior

- Global variables live in the global frame.
- Function calls push a new frame for parameters and local assignments.
- Variable lookup checks:
  - current function-local frame
  - then global frame
- Caller locals are never visible inside another function.
- Function definitions are stored globally.

## Current limitations

- Functions are type-checked on first successful call rather than from a separate compile pass.
- Blocks do not create independent nested variable scopes.
- Comparison is limited to numeric operands to match the project’s arithmetic-focused boolean expressions.

## Example

```txt
func countdown(n) {
    while (n > 0) {
        print(n);
        n = n - 1;
    }
    return n;
}

x = countdown(3);
print(x);
```

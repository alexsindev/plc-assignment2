# PLC Assignment 2 — Custom Language Compiler

A statically typed, lexically scoped programming language implemented in Python using SLY (lex/yacc) and a PySide6 IDE.

---

## Table of Contents

- [Dependencies](#dependencies)
- [Getting Started](#getting-started)
- [Running the IDE](#running-the-ide)
  - [VSCode Debugger](#vscode-debugger)
  - [VSCode Task](#vscode-task)
  - [Command Line](#command-line)
- [Module Structure](#module-structure)
- [Compiler Pipeline](#compiler-pipeline)
- [Language Reference](#language-reference)
  - [Types](#types)
  - [Grammar](#grammar)
  - [Typing](#typing)
  - [Scoping](#scoping)
  - [Parameter Passing](#parameter-passing)
  - [Binding](#binding)
  - [Known Limitations](#known-limitations)
- [Example Programs](#example-programs)

---

## Dependencies

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — project and environment management
- `sly` (from git master) — lexer and LR parser
- `PySide6` — IDE GUI

---

## Getting Started

```sh
git clone <repo>
cd plc-assignment2
uv sync
```

---

## Running the IDE

### VSCode Debugger

Open the Run and Debug panel (`Ctrl/Cmd + Shift + D`) and select **`[example] Python Debugger`**. This launches `src/example/main.py` with `debugpy` attached, so breakpoints in any module work.

The launch configuration is in [.vscode/launch.json](.vscode/launch.json):

```json
{
  "name": "[example] Python Debugger",
  "type": "debugpy",
  "request": "launch",
  "python": "${workspaceFolder}/.venv/bin/python",
  "program": "main.py",
  "cwd": "${workspaceFolder}/src/example/"
}
```

### VSCode Task

Open the command palette (`Ctrl/Cmd + Shift + P`), choose **Tasks: Run Task**, then **start app**. This runs `uv run main.py` from `src/example/`.

> The **start designer** and **compile designer** tasks exist in `.vscode/tasks.json` but are not needed — the GUI in `main.py` is built entirely in code, not from a `.ui` file. To change the UI, edit `main.py` directly.

### Command Line

```sh
cd src/example
uv run main.py
```

---

## Module Structure

```
src/example/
├── main.py                       # IDE entry point (PySide6 GUI)
└── components/
    ├── lexica.py                 # Lexer  — source text → token stream
    ├── parsers.py                # Parser — token stream → AST
    ├── type_checker.py           # Static type checker — AST → type errors
    ├── memory.py                 # Runtime memory — call stack, variables, functions
    ├── highlighter.py            # PySide6 syntax highlighter
    └── ast/
        └── statement.py          # AST node definitions (expressions + statements)

tests/
└── test_statements.py            # Pytest suite

examples/
├── 01_types.plc
├── 02_arithmetic.plc
├── 03_if_else.plc
├── 04_while.plc
├── 05_functions.plc
├── 06_static_type_binding.plc
└── 07_static_scope_binding.plc
```

### `lexica.py` — `MyLexer`

Extends `sly.Lexer`. Converts source text into a stream of tokens. Keywords (`if`, `else`, `while`, `func`, `return`, `print`, `true`, `false`) are matched by remapping the `NAME` token via `NAME["keyword"] = TOKEN`.

Tokens produced: `NUMBER`, `FLOAT`, `STRING`, `TRUE`, `FALSE`, `NAME`, `ASSIGN`, `PLUS`, `MINUS`, `TIMES`, `DIVIDE`, `LESS`, `LESS_EQUAL`, `GREATER`, `GREATER_EQUAL`, `EQUAL`, `NOT_EQUAL`, `LPAREN`, `RPAREN`, `LBRACE`, `RBRACE`, `COMMA`, `SEMI`, `IF`, `ELSE`, `WHILE`, `PRINT`, `FUNC`, `RETURN`.

### `parsers.py` — `ASTParser`

Extends `sly.Parser`. Implements an LR(1) parser with explicit operator precedence. Each grammar rule constructs and returns an AST node rather than evaluating immediately. The top-level rule returns a `Statement_block` representing the whole program.

Operator precedence (lowest → highest):

| Level | Operators | Associativity |
|-------|-----------|---------------|
| 1 | `==` `!=` `<` `<=` `>` `>=` | left |
| 2 | `+` `-` | left |
| 3 | `*` `/` | left |
| 4 | unary `-` | right |

### `ast/statement.py` — AST Nodes

All AST nodes implement `run(memory) -> object`. Execution is tree-walking: calling `.run()` on the root `Statement_block` recursively evaluates the entire program.

**Expression nodes** (return a value and set `self.data_type`):

| Class | Description |
|-------|-------------|
| `Expression_number` | Integer literal |
| `Expression_float` | Float literal |
| `Expression_boolean` | Boolean literal |
| `Expression_string` | String literal |
| `Expression_variable` | Variable read — looks up name in `Memory` |
| `Expression_math` | Binary arithmetic (`+` `-` `*` `/`) |
| `Expression_compare` | Binary comparison (`==` `!=` `<` `<=` `>` `>=`) |
| `Expression_call` | Function call — evaluates arguments, invokes `Statement_function.invoke()` |

**Statement nodes** (produce side effects):

| Class | Description |
|-------|-------------|
| `Statement_assignment` | Binds a name to a value in the current memory frame |
| `Statement_print` | Evaluates expression and appends to `Memory.output` |
| `Statement_if` | Conditional — evaluates condition, runs then or else block |
| `Statement_while` | Loop — evaluates condition before each iteration |
| `Statement_function` | Registers the function in `Memory.functions` |
| `Statement_return` | Raises `ReturnSignal` (caught by `Statement_function.invoke`) |
| `Statement_block` | Sequence of statements |
| `Statement_expression` | Expression used as a statement (e.g. a bare call) |

`ReturnSignal` is a custom exception used to unwind the call stack on `return`. It carries the return value and its `DataType`.

### `memory.py` — `Memory`

A singleton (via `__new__`) that holds the entire runtime state. Call `memory.reset()` before each program run.

**Call stack**: `stack: list[dict]` where `stack[0]` is the global frame. `push_frame()` / `pop_frame()` are called on function entry and exit. Each frame entry is `{ name: { "value": ..., "type": DataType } }`.

**Scope resolution** (`_lookup_frame`): checks the **current frame** first, then the **global frame** only — never intermediate frames. This enforces lexical scoping.

**Type stability** (`set`): if a name already exists in the current frame with a different type, `TypeError` is raised. A variable's type cannot change within its scope.

**Function registry**: functions are stored in `self.functions` (separate from the variable stack) and are globally accessible.

### `type_checker.py` — `TypeChecker`

A pre-execution static analysis pass. Call `TypeChecker().check(program)` on the parsed AST before calling `tree.run(memory)`.

**Two-pass algorithm:**

1. **Pass 1** — scans the top-level block and registers all `Statement_function` nodes by name, enabling forward calls.
2. **Pass 2** — walks every statement via `_check_stmt`, calling `_infer(expr)` to determine the `DataType` of each expression.

**Type inference (`_infer`):**

- Literals return their fixed type.
- `Expression_variable` looks up `_vars[name]` — raises `NameError` if used before assignment.
- `Expression_math` enforces same-type operands; returns `FLOAT` for division, else the operand type.
- `Expression_compare` enforces numeric operands; always returns `BOOL`.
- `Expression_call` infers argument types, locks them into the function signature on the first call, then checks the body (`_check_func_body`). Recursive calls are detected via `_in_progress` and return the partially-inferred return type.

**Variable locking:** on `Statement_assignment`, if `_vars` already contains a different type for the name, `TypeError` is raised.

### `highlighter.py` — `PLCSyntaxHighlighter`

Extends `QSyntaxHighlighter`. Applies `QRegularExpression` rules per line for keywords, literals, booleans, numbers, and strings in VSCode Dark+ colours.

### `main.py` — `CompilerIDE`

A `QMainWindow` with:
- Left pane: `QPlainTextEdit` code editor with syntax highlighting.
- Top-right pane: program output console.
- Bottom-right pane: error console.
- Toolbar: **Run**, **Clear**, **Open**, **Save**.

**Run pipeline** (inside `run_code()`):

```
source text
    → MyLexer().tokenize()       # token stream
    → ASTParser().parse()        # Statement_block (AST)
    → TypeChecker().check()      # static type errors raised here
    → tree.run(memory)           # execution; output collected in memory.output
```

Parse errors printed to stdout/stderr by SLY are captured with `contextlib.redirect_stdout/stderr` and routed to the error console.

---

## Compiler Pipeline

```
Source text
    │
    ▼
MyLexer.tokenize()          →  token stream (generator)
    │
    ▼
ASTParser.parse()           →  Statement_block (root AST node)
    │
    ▼
TypeChecker.check()         →  raises TypeError / NameError on violations
    │
    ▼
Statement_block.run(memory) →  tree-walking interpreter
    │
    ▼
memory.output               →  list of printed strings → GUI output pane
```

---

## Language Reference

### Types

| Type | Literal examples |
|------|-----------------|
| `int` | `0`, `42`, `-7` |
| `float` | `3.14`, `0.5` |
| `bool` | `true`, `false` |
| `string` | `"hello"` |
| `void` | (return type of functions with no return) |

### Grammar

```
<program>   ::= <stmts>

<stmts>     ::= <stmts> <stmt> | ε

<stmt>      ::= NAME ASSIGN <expr> SEMI
              | IF LPAREN <expr> RPAREN <block>
              | IF LPAREN <expr> RPAREN <block> ELSE <block>
              | WHILE LPAREN <expr> RPAREN <block>
              | PRINT LPAREN <expr> RPAREN SEMI
              | FUNC NAME LPAREN <params> RPAREN <block>
              | RETURN <expr> SEMI
              | <expr> SEMI

<block>     ::= LBRACE <stmts> RBRACE

<params>    ::= <params> COMMA NAME | NAME | ε

<expr>      ::= <expr> PLUS <expr>
              | <expr> MINUS <expr>
              | <expr> TIMES <expr>
              | <expr> DIVIDE <expr>
              | <expr> EQUAL <expr>
              | <expr> NOT_EQUAL <expr>
              | <expr> LESS <expr>
              | <expr> LESS_EQUAL <expr>
              | <expr> GREATER <expr>
              | <expr> GREATER_EQUAL <expr>
              | MINUS <expr>
              | LPAREN <expr> RPAREN
              | NAME LPAREN <args> RPAREN
              | NAME
              | NUMBER | FLOAT | TRUE | FALSE | STRING

<args>      ::= <args> COMMA <expr> | <expr> | ε
```

### Typing

The language is **statically typed with type inference** — no explicit type annotations are written. Types are inferred from usage.

- A variable's type is determined at its **first assignment** and cannot change.
- Arithmetic (`+` `-` `*` `/`) requires both operands to be the same type (`int` or `float`). No implicit coercion.
- Division (`/`) always produces `float`, even when both operands are `int`. The return type is determined statically by the operator, not by the runtime value.
- Comparisons (`==` `!=` `<` `<=` `>` `>=`) require both operands to be the same numeric type and always produce `bool`.
- `if` and `while` conditions must be `bool`.
- Function parameter types and return type are inferred at the **first call site** and locked for all subsequent calls.
- Type checking runs as a **pre-execution pass** (`TypeChecker`). Type errors are reported before any side effects occur.

### Scoping

The language uses **static (lexical) scoping**. A name is resolved in the environment where the function is **defined**, not where it is called.

The call stack (`Memory.stack`) holds frames, but name lookup (`_lookup_frame`) only ever checks two places: the **current function's frame** and the **global frame**. Intermediate caller frames are never visible.

```
x = 1;

func inner() {
    print(x);   # resolves x in global frame → 1
}

func outer() {
    x = 99;     # local to outer's frame
    inner();    # prints 1, not 99
}

outer();
```

A dynamically scoped language would make `inner` inherit `outer`'s `x = 99` and print `99`.

Functions are defined at **global scope only**. Nested function definitions are not permitted.

### Parameter Passing

Arguments are passed **by value**. At the call site, each argument expression is fully evaluated and the resulting value is copied into the callee's local frame. Modifying a parameter inside a function has no effect on the caller's variable.

```
x = 10;

func double(n) {
    n = n * 2;   # modifies local copy only
    return n;
}

print(double(x));   # 20
print(x);           # 10 — unchanged
```

### Binding

**Static variable binding** — a variable name is bound to exactly one type for its lifetime. The binding is established at first assignment and never changes.

**Static type binding** — the type of an expression is determined at compile time from the types of its operands, not from runtime values. The clearest example is division: `int / int` always produces `float` by static rule, even when the result is a whole number (`10 / 2 = 5.0`, not `5`).

**Static scope binding** — as described under [Scoping](#scoping), the scope chain is fixed at definition time.

### Known Limitations

- **Uncalled functions are not type-checked.** Because parameter types are inferred from call sites, a function that is never called has no type information to check against. Type errors in its body will not be caught statically. This is an inherent consequence of the inference strategy and is left as future work.
- **Branch-conditional variables.** A variable assigned only inside an `if` branch is added to the type environment by the type checker regardless of which branch executes. If the branch is not taken at runtime, accessing the variable will raise a `NameError`. Fixing this requires flow-sensitive typing.

---

## Example Programs

All examples are in the [`examples/`](examples/) directory and can be opened directly in the IDE.

| File | Demonstrates |
|------|-------------|
| `01_types.plc` | All four value types |
| `02_arithmetic.plc` | Arithmetic operators and precedence |
| `03_if_else.plc` | Conditional branching |
| `04_while.plc` | While loops |
| `05_functions.plc` | Function definition, recursion |
| `06_static_type_binding.plc` | Static vs dynamic type binding — how division always returns `float` |
| `07_static_scope_binding.plc` | Static vs dynamic scope — how callees resolve names from definition site |
| `08_pass_by_value.plc` | Pass by value — mutating a parameter inside a function does not affect the caller |

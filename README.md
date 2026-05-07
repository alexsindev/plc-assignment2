# PLC Assignment 2 — Custom Language Compiler

A statically typed, lexically scoped programming language implemented in Python using SLY (lex/yacc) and a PySide6 IDE.

---

## Table of Contents

- [Dependencies](#dependencies)
- [Getting Started](#getting-started)
- [CI and Branch Protection](#ci-and-branch-protection)
- [Running the IDE](#running-the-ide)
  - [VSCode Debugger](#vscode-debugger)
  - [VSCode Task](#vscode-task)
  - [Command Line](#command-line)
- [Running Tests](#running-tests)
- [Module Structure](#module-structure)
- [Compiler Pipeline](#compiler-pipeline)
- [Language Reference](#language-reference)
  - [Types](#types)
  - [Grammar](#grammar)
  - [Typing](#typing)
  - [Scoping](#scoping)
  - [Parameter Passing](#parameter-passing)
  - [Binding](#binding)
  - [Recursion](#recursion)
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

## CI and Branch Protection

A GitHub Actions workflow runs the full test suite on every pull request targeting `develop`. The workflow is defined in [.github/workflows/test.yml](.github/workflows/test.yml).

To enforce that PRs cannot be merged until CI passes:

1. Go to **Settings → Branches → Add branch protection rule**
2. Set the branch name pattern to `develop`
3. Enable **Require status checks to pass before merging**
4. Add `test` (the job name) as a required status check
5. Optionally enable **Require branches to be up to date before merging**

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

## Running Tests

```sh
uv run pytest tests/ -v
```

The test suite is split across five files:

| File | Coverage |
|------|----------|
| `tests/test_lexer.py` | Token types, literal values, keyword vs name disambiguation |
| `tests/test_parser.py` | AST node types and field values for every grammar rule |
| `tests/test_expressions.py` | Expression evaluation, operator precedence, type errors |
| `tests/test_statements.py` | Statement execution — happy path and error path for each statement type |
| `tests/test_integration.py` | Full-pipeline tests grouped by language feature (type binding, scope binding, pass by value, functions, control flow) — each section has happy path and error path |

Shared helpers (`parse`, `run_program`, `run_with_checker`, `assert_output`, `assert_raises`) are defined in `tests/conftest.py` and automatically available to all test files.

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
        └── statement.py         # AST node definitions (expressions + statements)

tests/
├── conftest.py                   # Shared helpers and sys.path setup
├── test_lexer.py
├── test_parser.py
├── test_expressions.py
├── test_statements.py
└── test_integration.py

examples/
├── 01_types.plc
├── 02_arithmetic.plc
├── 03_if_else.plc
├── 04_while.plc
├── 05_functions.plc
├── 06_static_type_binding.plc
├── 07_static_scope_binding.plc
└── 08_pass_by_value.plc
```

### `lexica.py` — `MyLexer`

Extends `sly.Lexer`. Converts source text into a stream of tokens. Keywords (`if`, `else`, `while`, `func`, `return`, `print`, `true`, `false`) are matched by remapping the `NAME` token via `NAME["keyword"] = TOKEN`.

Tokens produced: `NUMBER`, `FLOAT`, `STRING`, `TRUE`, `FALSE`, `NAME`, `ASSIGN`, `PLUS`, `MINUS`, `TIMES`, `DIVIDE`, `LESS`, `LESS_EQUAL`, `GREATER`, `GREATER_EQUAL`, `EQUAL`, `NOT_EQUAL`, `LPAREN`, `RPAREN`, `LBRACE`, `RBRACE`, `COMMA`, `SEMI`, `IF`, `ELSE`, `WHILE`, `PRINT`, `FUNC`, `RETURN`.

### `parsers.py` — `ASTParser`

Extends `sly.Parser`. Implements an LR(1) parser with explicit operator precedence. Each grammar rule constructs and returns an AST node rather than evaluating immediately. The top-level rule returns a `Statement_block` representing the whole program. On syntax error, SLY error-recovers and returns an empty `Statement_block`.

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
| `Expression_negate` | Unary minus — negates any numeric expression, preserving its type |
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

`Expression_negate` exists as a dedicated node (rather than sugar for `0 - x`) so that unary minus on a float does not create a type mismatch between an `INT` zero and a `FLOAT` operand.

### `memory.py` — `Memory`

A singleton (via `__new__`) that holds the entire runtime state. Call `memory.reset()` before each program run.

**Call stack**: `stack: list[dict]` where `stack[0]` is the global frame. `push_frame()` / `pop_frame()` are called on function entry and exit. Each frame entry is `{ name: { "value": ..., "type": DataType } }`.

**Scope resolution** (`_lookup_frame`): checks the **current frame** first, then the **global frame** only — never intermediate frames. This enforces lexical scoping.

**Type stability** (`set`): if a name already exists in the current frame with a different type, `TypeError` is raised. A variable's type cannot change within its scope.

**Function registry**: functions are stored in `self.functions` (separate from the variable stack) and are globally accessible.

### `type_checker.py` — `TypeChecker`

A pre-execution static analysis pass. Call `TypeChecker().check(program)` on the parsed AST before calling `tree.run(memory)`. All type errors are raised before any side effects occur.

**State:**

| Field | Type | Purpose |
|-------|------|---------|
| `_vars` | `dict[str, DataType]` | Maps variable names to their locked type. Set on first assignment; used to enforce static type binding on every subsequent read or write. |
| `_funcs` | `dict[str, _FuncSig]` | Maps function names to their signature record. Populated during the forward-reference pass so calls can appear before definitions. |
| `_in_progress` | `set[str]` | Names of functions currently being body-checked. Guards against infinite recursion when a function calls itself. |

**`_FuncSig` (dataclass):** holds a reference to the `Statement_function` AST node alongside the inferred `param_types` and `return_type`. Both start as `None` and are filled in on the first call to the function.

---

**`check(program)`** — public entry point. Runs two top-level passes over the program block:

1. **Forward-reference pass** — registers every top-level `Statement_function` in `_funcs` before any statement is checked. This allows a function to be called before its definition appears in the source.
2. **Check pass** — iterates every statement through `_check_stmt`.

---

**`_infer(expr) → DataType`** — central dispatch for expression type inference. Matches on the expression node type and returns its `DataType` without executing anything:

- `Expression_number` → `INT`
- `Expression_float` → `FLOAT`
- `Expression_boolean` → `BOOL`
- `Expression_string` → `STRING`
- `Expression_variable` → looks up `_vars[name]`; raises `NameError` if the variable has not been assigned yet
- `Expression_negate` → delegates to `_infer` on the operand; enforces numeric-only; returns the operand's type unchanged
- `Expression_math` → delegates to `_infer_math`
- `Expression_compare` → delegates to `_infer_compare`
- `Expression_call` → delegates to `_infer_call`

---

**`_infer_math(expr) → DataType`** — type rule for binary arithmetic:

1. Infers both operand types via `_infer`.
2. Raises `TypeError` if the two types differ (no implicit coercion).
3. Raises `TypeError` if the type is not `INT` or `FLOAT` (arithmetic is numeric-only).
4. Returns `FLOAT` unconditionally when the operator is `/`, otherwise returns the operand type. This is the static rule that makes `int / int` always `float` regardless of runtime value.

---

**`_infer_compare(expr) → DataType`** — type rule for binary comparison:

1. Infers both operand types via `_infer`.
2. Raises `TypeError` if the types differ.
3. Raises `TypeError` if the type is not `INT` or `FLOAT` (strings and booleans are not comparable).
4. Always returns `BOOL`.

---

**`_infer_call(expr) → DataType`** — type rule for function calls. This is the most complex inference step:

1. Raises `NameError` if the function name is not in `_funcs`.
2. Infers the type of each argument via `_infer`.
3. Raises `TypeError` on arity mismatch.
4. **First call:** locks `sig.param_types` to the inferred argument types.
5. **Subsequent calls:** raises `TypeError` if the argument types differ from the locked signature — function types are stable after first inference.
6. **Recursive call guard:** if the function name is already in `_in_progress`, returns `sig.return_type` (already seeded from the base case) instead of re-entering the body. This breaks the infinite recursion cycle.
7. **First call, non-recursive:** calls `_check_func_body` to check the body with the now-known parameter types, then returns the inferred return type.

---

**`_check_func_body(sig)`** — checks a function body in two passes, operating inside a temporary scope where parameters are pre-loaded into `_vars`:

- **Pass 1 — `_collect_returns`:** traverses every `return` statement in the body (recursing into `if`/`while`/blocks), infers the type of each returned expression, and verifies all return paths agree. As each return type is found, it is immediately written to `sig.return_type` — this seeds the type early so that recursive calls encountered in the same pass can resolve to the correct type rather than `VOID`.
- **Pass 2 — `_check_block`:** walks every statement in the body through `_check_stmt`, catching type errors in assignments, `print` calls, and bare expressions that `_collect_returns` skips.

The variable scope is saved before the two passes and restored afterwards, so local variables and parameters do not pollute the outer environment.

---

**`_collect_returns(block, sig) → list[DataType]`** — recursively gathers the `DataType` of every `return` statement reachable from `block`. Delegates each statement to `_returns_in`. The `sig` parameter is threaded through so `_returns_in` can seed `sig.return_type` incrementally.

---

**`_returns_in(stmt, sig) → list[DataType]`** — extracts return types from a single statement:

- `Statement_return` — infers the expression type; if `sig.return_type` is not yet set, sets it immediately (base-case seeding for recursive functions).
- `Statement_if` — recurses into the then-block and, if present, the else-block.
- `Statement_while` — recurses into the body.
- `Statement_block` — recurses into the nested block.
- All other statement types (assignments, `print`, etc.) — returns `[]`; these are handled separately by `_check_block` in Pass 2.

---

**`_check_stmt(stmt)`** — type-checks a single statement and updates `_vars` where applicable:

- `Statement_assignment` — infers the RHS expression type; raises `TypeError` if the variable already exists in `_vars` with a different type; otherwise records the type in `_vars`.
- `Statement_print` — infers the expression type (validates it is well-typed).
- `Statement_if` — infers the condition; raises `TypeError` if it is not `BOOL`; then calls `_check_block` on each branch.
- `Statement_while` — infers the condition; raises `TypeError` if it is not `BOOL`; then calls `_check_block` on the body.
- `Statement_return` — infers the expression type (validates it is well-typed).
- `Statement_function` — registers the function in `_funcs` if not already present.
- `Statement_expression` — infers the expression type to catch errors in bare calls.
- `Statement_block` — delegates to `_check_block`.

---

**`_check_block(block)`** — iterates every statement in a `Statement_block` through `_check_stmt`. The shared entry point for checking any sequence of statements, used by `_check_func_body` (Pass 2), `_check_stmt` for `if`/`while` branches, and `check` itself.

---

**Known gaps (by design):**

| Gap | Reason |
|-----|--------|
| Uncalled functions are not type-checked | Parameter types are inferred from the call site; with no call, there is nothing to infer from |
| Variables assigned in only one branch of `if`/`while` may not exist at runtime | Fixing this requires flow-sensitive typing, which is out of scope |

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
| `float` | `3.14`, `0.5`, `-1.0` |
| `bool` | `true`, `false` |
| `string` | `"hello"` |
| `void` | (return type of functions with no return statement) |

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

The language is **statically typed with type inference** — no explicit type annotations are written anywhere. Types are inferred from usage and locked statically before execution.

- A variable's type is determined at its **first assignment** and cannot change.
- Arithmetic (`+` `-` `*` `/`) requires both operands to be the same type (`int` or `float`). No implicit coercion between types.
- Division (`/`) always produces `float`, even when both operands are `int`. The return type is determined statically by the operator, not by the runtime value — `10 / 2` produces `5.0`, not `5`.
- Comparisons (`==` `!=` `<` `<=` `>` `>=`) require both operands to be the same numeric type and always produce `bool`. Strings and booleans cannot be compared.
- `if` and `while` conditions must be `bool`.
- Function parameter types and return type are inferred at the **first call site** and locked for all subsequent calls.
- Type checking runs as a **pre-execution pass** (`TypeChecker`). Type errors are reported before any side effects occur.

This approach is **call-site inference**: types flow from literal values at the call site into the function body, rather than being declared at function boundaries. It is less structured than local type inference (which requires annotations at function boundaries) but requires no annotations at all.

### Scoping

The language uses **static (lexical) scoping**. A name is resolved in the environment where the function is **defined**, not where it is called.

The call stack (`Memory.stack`) holds frames, but name lookup (`_lookup_frame`) only ever checks two places: the **current function's frame** and the **global frame**. Intermediate caller frames are never visible.

```
x = 1;

func inner() {
    print(x);   # resolves x in global frame → 1
}

func outer() {
    x = 99;     # local to outer's frame only
    inner();    # prints 1, not 99
}

outer();
```

A dynamically scoped language would make `inner` inherit `outer`'s `x = 99` and print `99`. With lexical scoping, `inner` always sees the global `x = 1` regardless of where it is called from.

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

Pass by reference would require storing a pointer back to the caller's frame slot instead of copying the value. In that model, `n = n * 2` inside the function would write back to `x` in the caller, making the final `print(x)` output `20`.

### Binding

**Static variable binding** — a variable name is bound to exactly one type for its lifetime. The binding is established at first assignment and never changes. Attempting to reassign a variable with a different type raises `TypeError`.

**Static type binding** — the type of an expression is determined at compile time from the types of its operands, not from runtime values. The clearest example is division: `int / int` always produces `float` by static rule, even when the result is a whole number (`10 / 2 = 5.0`, not `5`). A dynamically typed language could inspect the runtime value and return `int` when the division is exact.

**Static scope binding** — as described under [Scoping](#scoping), the scope chain is fixed at definition time and never changes regardless of call site.

### Recursion

Recursive functions are fully supported. The runtime handles recursion through the call stack — each recursive call pushes a new frame, executes the body, and pops on return. There is no explicit recursion limit beyond Python's own stack depth.

The type checker handles recursion via the `_in_progress` guard in `_infer_call`. When a recursive call is encountered mid-body-check, it returns `sig.return_type` (already seeded from the base case by `_collect_returns`) instead of re-entering the body, breaking the cycle.

```
func factorial(n) {
    if (n < 2) { return 1; }
    return n * factorial(n - 1);
}
print(factorial(5));   # 120
```

### Known Limitations

- **Uncalled functions are not type-checked.** Because parameter types are inferred from call sites, a function that is never called has no type information to check against. Type errors in its body will not be caught statically. This is an inherent consequence of the call-site inference strategy.
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
| `06_static_type_binding.plc` | Static vs dynamic type binding — how `int / int` always returns `float` |
| `07_static_scope_binding.plc` | Static vs dynamic scope — how callees resolve names from their definition site |
| `08_pass_by_value.plc` | Pass by value — mutating a parameter inside a function does not affect the caller |

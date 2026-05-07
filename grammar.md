### Grammar of the language in BNF

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

### Operator precedence (lowest to highest)

| Level | Operators | Associativity |
|-------|-----------|---------------|
| 1 | `==`  `!=`  `<`  `<=`  `>`  `>=` | left |
| 2 | `+`  `-` | left |
| 3 | `*`  `/` | left |
| 4 | unary `-` | right |

### Type rules

- Types are inferred from the first assignment; no explicit declaration.
- A variable's type is fixed at first assignment — reassigning with a different type is a TypeError.
- Arithmetic (`+` `-` `*` `/`) requires both operands to be the same type and INT or FLOAT.
- Comparisons (`==` `!=` `<` `<=` `>` `>=`) require both operands to be the same type and INT or FLOAT.
- `if` and `while` conditions must evaluate to BOOL (i.e. the expression must be a comparison).
- Division always produces FLOAT, even when both operands are INT.
- Function parameter types and return type are inferred on the first call and locked for all subsequent calls.
- Functions are defined in global scope only. Scoping is lexical: functions see their own locals and globals, never the caller's locals.

### Grammar of the language in BNF

```
<program>   ::= <defs> <stmts>

<defs>      ::= <defs> <def> | ε

<def>       ::= FUNC ID LPAREN <params> RPAREN LBRACE <stmts> RBRACE

<params>    ::= <params> COMMA ID | ID | ε

<stmts>     ::= <stmts> <stmt> | ε

<stmt>      ::= ID ASSIGN <expr> SEMI
              | IF <bool_expr> LBRACE <stmts> RBRACE
              | IF <bool_expr> LBRACE <stmts> RBRACE ELSE LBRACE <stmts> RBRACE
              | WHILE <bool_expr> LBRACE <stmts> RBRACE
              | PRINT LPAREN <expr> RPAREN SEMI
              | ID LPAREN <args> RPAREN SEMI
              | RETURN <expr> SEMI

<bool_expr> ::= <expr> EQ <expr>
              | <expr> NEQ <expr>
              | <expr> LT <expr>
              | <expr> LE <expr>
              | <expr> GT <expr>
              | <expr> GE <expr>

<expr>      ::= <expr> PLUS <expr>
              | <expr> MINUS <expr>
              | <expr> TIMES <expr>
              | <expr> DIVIDE <expr>
              | LPAREN <expr> RPAREN
              | ID LPAREN <args> RPAREN
              | ID
              | INT | FLOAT | BOOL | STRING

<args>      ::= <args> COMMA <expr> | <expr> | ε
```

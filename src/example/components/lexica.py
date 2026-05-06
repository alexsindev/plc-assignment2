from sly import Lexer
import sly


class MyLexer(Lexer):
    """
    Lexer for the project language.
    Supports literals, arithmetic/comparison operators, and statement keywords.
    """

    tokens = {
        ASSIGN,
        NAME,
        NUMBER,
        FLOAT,
        STRING,
        TRUE,
        FALSE,
        IF,
        ELSE,
        WHILE,
        PRINT,
        FUNC,
        RETURN,
        PLUS,
        MINUS,
        TIMES,
        DIVIDE,
        LESS,
        LESS_EQUAL,
        GREATER,
        GREATER_EQUAL,
        EQUAL,
        NOT_EQUAL,
        LPAREN,
        RPAREN,
        LBRACE,
        RBRACE,
        COMMA,
        SEMI,
    }

    ignore = " \t"

    NAME = r"[a-zA-Z_][a-zA-Z0-9_]*"
    NAME["true"] = TRUE
    NAME["false"] = FALSE
    NAME["if"] = IF
    NAME["else"] = ELSE
    NAME["while"] = WHILE
    NAME["print"] = PRINT
    NAME["func"] = FUNC
    NAME["return"] = RETURN

    LESS_EQUAL = r"<="
    GREATER_EQUAL = r">="
    EQUAL = r"=="
    NOT_EQUAL = r"!="
    ASSIGN = r"="
    LESS = r"<"
    GREATER = r">"
    LPAREN = r"\("
    RPAREN = r"\)"
    LBRACE = r"\{"
    RBRACE = r"\}"
    COMMA = r","
    SEMI = r";"
    PLUS = r"\+"
    MINUS = r"-"
    TIMES = r"\*"
    DIVIDE = r"/"

    @_(r"\d+\.\d+")
    def FLOAT(self, token):
        token.value = float(token.value)
        return token

    @_(r"\d+")
    def NUMBER(self, token):
        token.value = int(token.value)
        return token

    @_(r'"[^"\n]*"')
    def STRING(self, token):
        token.value = token.value[1:-1]
        return token

    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        self.index += 1
        print(f"ERROR: Illegal character '{t.value[0]}' at line {self.lineno}")


if __name__ == "__main__":
    def run_lexer_test(text, expected_tokens):
        lex = MyLexer()
        tokens = [token.type for token in lex.tokenize(text)]
        assert tokens == expected_tokens, (
            f"FAILED: {text}\nExpected: {expected_tokens}\nGot: {tokens}"
        )
        print(f"PASSED: {text} -> {tokens}")

    run_lexer_test("5 + 3;", ["NUMBER", "PLUS", "NUMBER", "SEMI"])
    run_lexer_test("3.14 + 2", ["FLOAT", "PLUS", "NUMBER"])
    run_lexer_test("true false", ["TRUE", "FALSE"])
    run_lexer_test("abc xyz", ["NAME", "NAME"])
    run_lexer_test('"hello"', ["STRING"])
    run_lexer_test("x <= 10", ["NAME", "LESS_EQUAL", "NUMBER"])
    run_lexer_test("x == y", ["NAME", "EQUAL", "NAME"])
    run_lexer_test(
        "if (x < 2) { print(x); }",
        [
            "IF",
            "LPAREN",
            "NAME",
            "LESS",
            "NUMBER",
            "RPAREN",
            "LBRACE",
            "PRINT",
            "LPAREN",
            "NAME",
            "RPAREN",
            "SEMI",
            "RBRACE",
        ],
    )

    print("\nAll lexer tests passed.")

    string_input: str = "x1 + 1as! * ()"
    lex: Lexer = MyLexer()
    token: sly.lex.Token
    for token in lex.tokenize(string_input):
        print(token)

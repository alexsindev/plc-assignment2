from conftest import ROOT, MyLexer


def tokens(text: str) -> list[str]:
    return [t.type for t in MyLexer().tokenize(text)]


def token_values(text: str):
    return [(t.type, t.value) for t in MyLexer().tokenize(text)]


def test_keywords():
    assert tokens("if else while func return print true false") == [
        "IF", "ELSE", "WHILE", "FUNC", "RETURN", "PRINT", "TRUE", "FALSE",
    ]


def test_comparison_operators():
    assert tokens("== != < <= > >=") == [
        "EQUAL", "NOT_EQUAL", "LESS", "LESS_EQUAL", "GREATER", "GREATER_EQUAL",
    ]


def test_arithmetic_operators():
    assert tokens("+ - * /") == ["PLUS", "MINUS", "TIMES", "DIVIDE"]


def test_punctuation():
    assert tokens("( ) { } , ; =") == [
        "LPAREN", "RPAREN", "LBRACE", "RBRACE", "COMMA", "SEMI", "ASSIGN",
    ]


def test_integer_literal_value():
    pairs = token_values("0 42 100")
    assert pairs == [("NUMBER", 0), ("NUMBER", 42), ("NUMBER", 100)]


def test_float_literal_value():
    pairs = token_values("3.14 0.5 1.0")
    assert pairs == [("FLOAT", 3.14), ("FLOAT", 0.5), ("FLOAT", 1.0)]


def test_string_literal_strips_quotes():
    pairs = token_values('"hello" "world"')
    assert pairs == [("STRING", "hello"), ("STRING", "world")]


def test_boolean_literal_types():
    assert tokens("true false") == ["TRUE", "FALSE"]


def test_name_token():
    pairs = token_values("x myVar _count")
    assert pairs == [("NAME", "x"), ("NAME", "myVar"), ("NAME", "_count")]


def test_name_not_confused_with_keyword_prefix():
    pairs = token_values("iffy whileTrue functions")
    assert all(t == "NAME" for t, _ in pairs)


def test_compound_if_statement():
    assert tokens('if (x < 2) { print("ok"); }') == [
        "IF", "LPAREN", "NAME", "LESS", "NUMBER",
        "RPAREN", "LBRACE", "PRINT", "LPAREN", "STRING", "RPAREN", "SEMI", "RBRACE",
    ]


def test_function_definition_tokens():
    assert tokens("func add(a, b) { return a + b; }") == [
        "FUNC", "NAME", "LPAREN", "NAME", "COMMA", "NAME",
        "RPAREN", "LBRACE", "RETURN", "NAME", "PLUS", "NAME", "SEMI", "RBRACE",
    ]

from sly import Lexer
import sly

class MyLexer(Lexer):
    """
    MyLexer is a class that inherits from sly.Lexer
    It is used to tokenize the input string.
    ref: https://sly.readthedocs.io/en/latest/sly.html#sly-sly-lex-yacc
    

    Python regEX: https://www.w3schools.com/python/python_regex.asp
    """

    ### `tokens` ###
    # set `tokens` so it can be used in the parser.
    # This must be here and all Capitalized. 
    # Please, ignore IDE warning.
    tokens = {
        ASSIGN,

        NAME,
        NUMBER,
        FLOAT,
        STRING,

        TRUE,
        FALSE,

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
   }
    
    ### matching rule ###
    # The matching work from top to bottom
    # At least, all toekns must be defined here

    # Ignore spaces and tabs 
    ignore = ' \t'

    ### EX1: simply define with regEX ###
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NAME['true'] = TRUE
    NAME['false'] = FALSE

    # Try uncomment this and run to see the differences between `token` and `literal`
    
    LESS_EQUAL = r'<='
    GREATER_EQUAL = r'>='
    EQUAL = r'=='
    NOT_EQUAL = r'!='
    ASSIGN  = r'\='
    LESS = r'<'
    GREATER = r'>'
    LPAREN = r'\('
    RPAREN = r'\)'
    PLUS    = r'\+'
    MINUS   = r'-'
    TIMES   = r'\*'
    DIVIDE  = r'/'


    # Extra action for newlines
    @_(r'\n+')
    def ignore_newline(self, t):
        # https://sly.readthedocs.io/en/latest/sly.html#line-numbers-and-position-tracking
        self.lineno += t.value.count('\n')

    def error(self, t):
        self.index += 1
        print(f"ERROR: Illegal character '{t.value[0]}' at line {self.lineno}")

    @_(r'\d+\.\d+')
    def FLOAT(self, token):
        token.value = float(token.value)
        return token
    
    ### EX2: Define as a function ###
    @_(r'\d+')
    def NUMBER(self, token):
        # Note that this function set parse token.value to integer
        token.value = int(token.value)
        # Extra print for debug
        print(f"====This print from NUMBER function: {token.type=} {token.value=} {type(token.value)=}")
        return token
    
    @_(r'"[^"]*"')
    def STRING(self, token):
        token.value = token.value[1:-1]
        return token

if __name__ == '__main__':
    # Write a simple test that only run when you execute this file
    def run_lexer_test(text, expected_tokens):
        lex = MyLexer()

        tokens = [
            token.type
            for token in lex.tokenize(text)
        ]

        assert tokens == expected_tokens, (
            f"FAILED: {text}\n"
            f"Expected: {expected_tokens}\n"
            f"Got: {tokens}"
        )

        print(f"PASSED: {text} -> {tokens}")

    # Arithmetic
    run_lexer_test(
        "5 + 3",
        ["NUMBER", "PLUS", "NUMBER"]
    )

    # Float
    run_lexer_test(
        "3.14 + 2",
        ["FLOAT", "PLUS", "NUMBER"]
    )

    # Boolean
    run_lexer_test(
        "true false",
        ["TRUE", "FALSE"]
    )

    # Variables
    run_lexer_test(
        "abc xyz",
        ["NAME", "NAME"]
    )

    # String
    run_lexer_test(
        '"hello"',
        ["STRING"]
    )

    # Comparison
    run_lexer_test(
        "x <= 10",
        ["NAME", "LESS_EQUAL", "NUMBER"]
    )

    # Equality
    run_lexer_test(
        "x == y",
        ["NAME", "EQUAL", "NAME"]
    )

    # Parentheses
    run_lexer_test(
        "(5 + 3)",
        ["LPAREN", "NUMBER", "PLUS", "NUMBER", "RPAREN"]
    )

    print("\nAll lexer tests passed.")
    
    string_input:str = "x1 + 1as! * ()"
    lex:Lexer = MyLexer()
    # assign type to `token`
    token: sly.lex.Token
    for token in lex.tokenize(string_input):
        print(token)
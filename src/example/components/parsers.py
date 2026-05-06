from components.lexica import MyLexer
from components.memory import Memory
from sly import Parser

class MyParser(Parser):
    debugfile = 'parser.out'
    start = 'statement'
    # Get the token list from the lexer (required)
    tokens = MyLexer.tokens
    precedence = (
    ('left', LESS, LESS_EQUAL, GREATER, GREATER_EQUAL, EQUAL, NOT_EQUAL),
    ('left', PLUS, MINUS),
    ('left', TIMES, DIVIDE),
    ('right', UMINUS),
    )
    
    def __init__(self):
        self.memory:Memory = Memory()

    @_('NAME ASSIGN expr')
    def statement(self, p):
        var_name = p.NAME
        value = p.expr
        self.memory.set(variable_name=var_name,value=value, data_type=type(value))
        # Note that I did not return anything

    @_('expr')
    # S -> E
    def statement(self, p) -> int:
        return p.expr

    # The example with literals
    @_('expr PLUS expr')
    # E -> E + E
    def expr(self, p):
        # You can refer to the token 2 ways
        # Way1: using array
        print(p[0], p[1], p[2])
        # Way2: using symbol name. 
        # Here, if you have more than one symbols with the same name
        # You have to indiciate the number at the end.
        return p.expr0 + p.expr1

    # The example with normal token
    @_('expr MINUS expr')
    def expr(self, p):
        print(p[0], p[1], p[2])
        return p.expr0 - p.expr1

    @_('expr TIMES expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr DIVIDE expr')
    def expr(self, p):
        return p.expr0 / p.expr1

    # https://sly.readthedocs.io/en/latest/sly.html#dealing-with-ambiguous-grammars
    # `%prec UMINUS` is the way to override the `precedence` of MINUS to UMINUS.
    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return -p.expr

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('NUMBER')
    def expr(self, p):
        return int(p.NUMBER)


from components.ast.statement import (
    Expression,
    Expression_math,
    Expression_number,
    Expression_float,
    Expression_boolean,
    Expression_string,
    Expression_variable,
    Expression_compare,
    Operations,
    CompareOperations
)
class ASTParser(Parser):
    debugfile = 'parser.out'
    start = 'statement'
    # Get the token list from the lexer (required)
    tokens = MyLexer.tokens
    precedence = (
    ('left', LESS, LESS_EQUAL, GREATER, GREATER_EQUAL, EQUAL, NOT_EQUAL),
    ('left', PLUS, MINUS),
    ('left', TIMES, DIVIDE),
    ('right', UMINUS),
    )

    @_('expr')
    def statement(self, p) -> int:
        p.expr.run()
        return p.expr.value

    @_('expr PLUS expr')
    def expr(self, p) -> Expression:
        parameter1 = p.expr0
        parameter2 = p.expr1
        expr = Expression_math(operation=Operations.PLUS, parameter1=parameter1, parameter2=parameter2)
        return expr
    
    @_('expr MINUS expr')
    def expr(self, p) -> Expression:
        parameter1 = p.expr0
        parameter2 = p.expr1
        expr = Expression_math(operation=Operations.MINUS, parameter1=parameter1, parameter2=parameter2)
        return expr
    
    @_('expr TIMES expr')
    def expr(self, p) -> Expression:
        return Expression_math(
            operation=Operations.TIMES,
            parameter1=p.expr0,
            parameter2=p.expr1
        )

    @_('expr DIVIDE expr')
    def expr(self, p) -> Expression:
        return Expression_math(
            operation=Operations.DIVIDE,
            parameter1=p.expr0,
            parameter2=p.expr1
        )
    @_('FLOAT')
    def expr(self, p) -> Expression:
        return Expression_float(number=p.FLOAT)

    @_('TRUE')
    def expr(self, p) -> Expression:
        return Expression_boolean(True)

    @_('FALSE')
    def expr(self, p) -> Expression:
        return Expression_boolean(False)

    @_('NUMBER')
    def expr(self, p) -> Expression:
        return Expression_number(number=p.NUMBER)
        
    @_('STRING')
    def expr(self, p) -> Expression:
        return Expression_string(text=p.STRING) 
    
    @_('NAME')
    def expr(self, p) -> Expression:
        return Expression_variable(
            variable_name=p.NAME
        )

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr
    
    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return Expression_math(
            operation=Operations.MINUS,
            parameter1=Expression_number(0),
            parameter2=p.expr
        )
    
    @_('expr LESS expr')
    def expr(self, p):
        return Expression_compare(
            operation=CompareOperations.LESS,
            parameter1=p.expr0,
            parameter2=p.expr1
        )
    
    @_('expr LESS_EQUAL expr')
    def expr(self, p):
        return Expression_compare(
            operation=CompareOperations.LESS_EQUAL,
            parameter1=p.expr0,
            parameter2=p.expr1
        )
        
    @_('expr GREATER expr')
    def expr(self, p):
        return Expression_compare(
            operation=CompareOperations.GREATER,
            parameter1=p.expr0,
            parameter2=p.expr1
        )
    
    @_('expr GREATER_EQUAL expr')
    def expr(self, p):
        return Expression_compare(
            operation=CompareOperations.GREATER_EQUAL,
            parameter1=p.expr0,
            parameter2=p.expr1
        )
    
    @_('expr EQUAL expr')
    def expr(self, p):
        return Expression_compare(
            operation=CompareOperations.EQUAL,
            parameter1=p.expr0,
            parameter2=p.expr1
        )

    @_('expr NOT_EQUAL expr')
    def expr(self, p):
        return Expression_compare(
            operation=CompareOperations.NOT_EQUAL,
            parameter1=p.expr0,
            parameter2=p.expr1
        )
if __name__ == "__main__":
    lexer = MyLexer()
    # parser = MyParser()
    text = "9 + 2 + 3"
    memory = Memory()
    parser = ASTParser()
    # text = "1 + 2 + 3"
    def run_test(text, expected):
        lexer = MyLexer()
        parser = ASTParser()

        result = parser.parse(lexer.tokenize(text))

        assert result == expected, (
            f"FAILED: {text}\n"
            f"Expected: {expected}\n"
            f"Got: {result}"
        )

        print(f"PASSED: {text} -> {result}")
    # Arithmetic
    run_test("5 + 3", 8)
    run_test("10 - 2", 8)

    # Precedence
    run_test("5 + 3 * 2", 11)
    run_test("(5 + 3) * 2", 16)

    # Float
    run_test("3.5 + 2.5", 6.0)

    # Comparison
    run_test("5 < 10", True)
    run_test("5 == 5", True)

    # Boolean
    run_test("true", True)

    # String
    run_test('"hello"', "hello")

    # Type error test
    try:
        run_test('5 + "hello"', None)
        assert False, "Expected TypeError"

    except TypeError:
        print("PASSED: Type mismatch detected")

    print("\nAll tests passed.")

    result = parser.parse(lexer.tokenize(text))
    print(result)
    # print(memory)
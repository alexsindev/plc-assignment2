from sly import Parser

from components.ast.statement import (
    CompareOperations,
    Expression,
    Expression_boolean,
    Expression_call,
    Expression_compare,
    Expression_float,
    Expression_math,
    Expression_negate,
    Expression_number,
    Expression_string,
    Expression_variable,
    Operations,
    Statement_assignment,
    Statement_block,
    Statement_expression,
    Statement_function,
    Statement_if,
    Statement_print,
    Statement_return,
    Statement_while,
)
from components.lexica import MyLexer



class ASTParser(Parser):
    debugfile = "parser.out"
    start = "program"
    tokens = MyLexer.tokens
    precedence = (
        ("left", LESS, LESS_EQUAL, GREATER, GREATER_EQUAL, EQUAL, NOT_EQUAL),
        ("left", PLUS, MINUS),
        ("left", TIMES, DIVIDE),
        ("right", UMINUS),
    )

    @_('statements')
    def program(self, p):
        return Statement_block(p.statements)

    @_('')
    def program(self, p):
        return Statement_block([])

    @_('statements statement')
    def statements(self, p):
        return p.statements + [p.statement]

    @_('statement')
    def statements(self, p):
        return [p.statement]

    @_('assignment_statement')
    def statement(self, p):
        return p.assignment_statement

    @_('print_statement')
    def statement(self, p):
        return p.print_statement

    @_('if_statement')
    def statement(self, p):
        return p.if_statement

    @_('while_statement')
    def statement(self, p):
        return p.while_statement

    @_('function_statement')
    def statement(self, p):
        return p.function_statement

    @_('return_statement')
    def statement(self, p):
        return p.return_statement

    @_('block')
    def statement(self, p):
        return p.block

    @_('expr SEMI')
    def statement(self, p):
        return Statement_expression(p.expr)

    @_('expr')
    def statement(self, p):
        return Statement_expression(p.expr)

    @_('NAME ASSIGN expr SEMI')
    def assignment_statement(self, p):
        return Statement_assignment(variable_name=p.NAME, expression=p.expr)

    @_('NAME ASSIGN expr')
    def assignment_statement(self, p):
        return Statement_assignment(variable_name=p.NAME, expression=p.expr)

    @_('PRINT LPAREN expr RPAREN SEMI')
    def print_statement(self, p):
        return Statement_print(expression=p.expr)

    @_('IF LPAREN expr RPAREN block ELSE block')
    def if_statement(self, p):
        return Statement_if(condition=p.expr, then_block=p.block0, else_block=p.block1)

    @_('IF LPAREN expr RPAREN block')
    def if_statement(self, p):
        return Statement_if(condition=p.expr, then_block=p.block)

    @_('WHILE LPAREN expr RPAREN block')
    def while_statement(self, p):
        return Statement_while(condition=p.expr, body=p.block)

    @_('FUNC NAME LPAREN parameters RPAREN block')
    def function_statement(self, p):
        return Statement_function(
            function_name=p.NAME,
            parameters=p.parameters,
            body=p.block,
        )

    @_('RETURN expr SEMI')
    def return_statement(self, p):
        return Statement_return(expression=p.expr)

    @_('LBRACE statements RBRACE')
    def block(self, p):
        return Statement_block(p.statements)

    @_('LBRACE RBRACE')
    def block(self, p):
        return Statement_block([])

    @_('parameter_items')
    def parameters(self, p):
        return p.parameter_items

    @_('')
    def parameters(self, p):
        return []

    @_('parameter_items COMMA NAME')
    def parameter_items(self, p):
        return p.parameter_items + [p.NAME]

    @_('NAME')
    def parameter_items(self, p):
        return [p.NAME]

    @_('argument_items')
    def arguments(self, p):
        return p.argument_items

    @_('')
    def arguments(self, p):
        return []

    @_('argument_items COMMA expr')
    def argument_items(self, p):
        return p.argument_items + [p.expr]

    @_('expr')
    def argument_items(self, p):
        return [p.expr]

    @_('expr PLUS expr')
    def expr(self, p) -> Expression:
        return Expression_math(
            operation=Operations.PLUS,
            parameter1=p.expr0,
            parameter2=p.expr1,
        )

    @_('expr MINUS expr')
    def expr(self, p) -> Expression:
        return Expression_math(
            operation=Operations.MINUS,
            parameter1=p.expr0,
            parameter2=p.expr1,
        )

    @_('expr TIMES expr')
    def expr(self, p) -> Expression:
        return Expression_math(
            operation=Operations.TIMES,
            parameter1=p.expr0,
            parameter2=p.expr1,
        )

    @_('expr DIVIDE expr')
    def expr(self, p) -> Expression:
        return Expression_math(
            operation=Operations.DIVIDE,
            parameter1=p.expr0,
            parameter2=p.expr1,
        )

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return Expression_negate(p.expr)

    @_('expr LESS expr')
    def expr(self, p):
        return Expression_compare(
            operation=CompareOperations.LESS,
            parameter1=p.expr0,
            parameter2=p.expr1,
        )

    @_('expr LESS_EQUAL expr')
    def expr(self, p):
        return Expression_compare(
            operation=CompareOperations.LESS_EQUAL,
            parameter1=p.expr0,
            parameter2=p.expr1,
        )

    @_('expr GREATER expr')
    def expr(self, p):
        return Expression_compare(
            operation=CompareOperations.GREATER,
            parameter1=p.expr0,
            parameter2=p.expr1,
        )

    @_('expr GREATER_EQUAL expr')
    def expr(self, p):
        return Expression_compare(
            operation=CompareOperations.GREATER_EQUAL,
            parameter1=p.expr0,
            parameter2=p.expr1,
        )

    @_('expr EQUAL expr')
    def expr(self, p):
        return Expression_compare(
            operation=CompareOperations.EQUAL,
            parameter1=p.expr0,
            parameter2=p.expr1,
        )

    @_('expr NOT_EQUAL expr')
    def expr(self, p):
        return Expression_compare(
            operation=CompareOperations.NOT_EQUAL,
            parameter1=p.expr0,
            parameter2=p.expr1,
        )

    @_('NAME LPAREN arguments RPAREN')
    def expr(self, p):
        return Expression_call(function_name=p.NAME, arguments=p.arguments)

    @_('FLOAT')
    def expr(self, p):
        return Expression_float(number=p.FLOAT)

    @_('TRUE')
    def expr(self, p):
        return Expression_boolean(True)

    @_('FALSE')
    def expr(self, p):
        return Expression_boolean(False)

    @_('NUMBER')
    def expr(self, p):
        return Expression_number(number=p.NUMBER)

    @_('STRING')
    def expr(self, p):
        return Expression_string(text=p.STRING)

    @_('NAME')
    def expr(self, p):
        return Expression_variable(variable_name=p.NAME)

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr


if __name__ == "__main__":
    from components.memory import Memory

    def parse_and_run(text):
        memory = Memory()
        memory.reset()
        tree = ASTParser().parse(MyLexer().tokenize(text))
        result = tree.run(memory)
        return result, memory

    result, memory = parse_and_run("x = 1; while (x < 3) { print(x); x = x + 1; }")
    assert memory.output == ["1", "2"]
    assert memory.get("x") == 3
    print(result)
    print(memory)

from conftest import parse
from components.ast.statement import (
    Expression_call,
    Expression_math,
    Operations,
    Statement_assignment,
    Statement_block,
    Statement_function,
    Statement_if,
    Statement_print,
    Statement_return,
    Statement_while,
)


def test_empty_program_is_empty_block():
    tree = parse("")
    assert isinstance(tree, Statement_block)
    assert tree.statements == []


def test_assignment_node():
    tree = parse("x = 5;")
    stmt = tree.statements[0]
    assert isinstance(stmt, Statement_assignment)
    assert stmt.variable_name == "x"


def test_print_node():
    tree = parse("print(42);")
    assert isinstance(tree.statements[0], Statement_print)


def test_function_definition_node():
    tree = parse("func add(a, b) { return a + b; }")
    stmt = tree.statements[0]
    assert isinstance(stmt, Statement_function)
    assert stmt.function_name == "add"
    assert stmt.parameters == ["a", "b"]
    assert isinstance(stmt.body, Statement_block)


def test_function_no_params():
    tree = parse("func greet() { return 1; }")
    stmt = tree.statements[0]
    assert stmt.parameters == []


def test_if_node():
    tree = parse("if (x < 2) { print(x); }")
    assert isinstance(tree.statements[0], Statement_if)
    assert tree.statements[0].else_block is None


def test_if_else_node():
    tree = parse("if (x < 2) { print(x); } else { print(x); }")
    stmt = tree.statements[0]
    assert isinstance(stmt, Statement_if)
    assert stmt.else_block is not None


def test_while_node():
    tree = parse("while (x < 10) { x = x + 1; }")
    assert isinstance(tree.statements[0], Statement_while)


def test_return_node():
    tree = parse("func f(x) { return x; }")
    body = tree.statements[0].body
    assert isinstance(body.statements[0], Statement_return)


def test_arithmetic_expression_node():
    tree = parse("z = 3 + 4;")
    expr = tree.statements[0].expression
    assert isinstance(expr, Expression_math)
    assert expr.operation == Operations.PLUS


def test_function_call_expression_node():
    tree = parse("func f(x) { return x; } y = f(1);")
    call_expr = tree.statements[1].expression
    assert isinstance(call_expr, Expression_call)
    assert call_expr.function_name == "f"
    assert len(call_expr.arguments) == 1


def test_invalid_syntax_produces_empty_block():
    # SLY error-recovers rather than returning None; the result is an empty block.
    tree = parse("func {")
    assert isinstance(tree, Statement_block)
    assert tree.statements == []


def test_multiple_statements_in_block():
    tree = parse("x = 1; y = 2; z = 3;")
    assert len(tree.statements) == 3

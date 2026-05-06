from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "example"))

from components.ast.expression import (
    CompareOperations,
    DataType,
    Expression_boolean,
    Expression_call,
    Expression_compare,
    Expression_float,
    Expression_math,
    Expression_number,
    Expression_string,
    Expression_variable,
    Operations,
)
from components.ast.statement import Statement_block, Statement_function, Statement_return
from components.memory import Memory


def fresh_memory():
    memory = Memory()
    memory.reset()
    return memory


def assert_raises(exc_type, expected_message, fn):
    try:
        fn()
    except exc_type as exc:
        assert expected_message in str(exc)
        return
    assert False, f"Expected {exc_type.__name__} containing: {expected_message}"


def test_int_literal_expression():
    expr = Expression_number(7)
    value = expr.run(fresh_memory())
    assert value == 7
    assert expr.data_type == DataType.INT


def test_float_literal_expression():
    expr = Expression_float(3.5)
    value = expr.run(fresh_memory())
    assert value == 3.5
    assert expr.data_type == DataType.FLOAT


def test_boolean_literal_expression():
    expr = Expression_boolean(True)
    value = expr.run(fresh_memory())
    assert value is True
    assert expr.data_type == DataType.BOOL


def test_string_literal_expression():
    expr = Expression_string("hello")
    value = expr.run(fresh_memory())
    assert value == "hello"
    assert expr.data_type == DataType.STRING


def test_math_expression_addition_preserves_int_type():
    expr = Expression_math(
        Operations.PLUS,
        Expression_number(5),
        Expression_number(3),
    )
    value = expr.run(fresh_memory())
    assert value == 8
    assert expr.data_type == DataType.INT


def test_math_expression_division_returns_float_type():
    expr = Expression_math(
        Operations.DIVIDE,
        Expression_number(5),
        Expression_number(2),
    )
    value = expr.run(fresh_memory())
    assert value == 2.5
    assert expr.data_type == DataType.FLOAT


def test_math_expression_rejects_type_mismatch():
    expr = Expression_math(
        Operations.PLUS,
        Expression_number(5),
        Expression_float(2.0),
    )
    assert_raises(TypeError, "Type mismatch", lambda: expr.run(fresh_memory()))


def test_comparison_expression_returns_bool():
    expr = Expression_compare(
        CompareOperations.LESS,
        Expression_number(2),
        Expression_number(4),
    )
    value = expr.run(fresh_memory())
    assert value is True
    assert expr.data_type == DataType.BOOL


def test_comparison_expression_rejects_non_numeric_operands():
    expr = Expression_compare(
        CompareOperations.EQUAL,
        Expression_string("a"),
        Expression_string("b"),
    )
    assert_raises(TypeError, "Comparisons only support int and float", lambda: expr.run(fresh_memory()))


def test_variable_expression_reads_from_memory():
    memory = fresh_memory()
    memory.set("x", 9, DataType.INT)
    expr = Expression_variable("x")
    value = expr.run(memory)
    assert value == 9
    assert expr.data_type == DataType.INT


def test_variable_expression_raises_for_unknown_name():
    expr = Expression_variable("missing")
    assert_raises(NameError, "is not defined", lambda: expr.run(fresh_memory()))


def test_expression_call_invokes_function_and_returns_value():
    memory = fresh_memory()
    function_stmt = Statement_function(
        "identity",
        ["value"],
        Statement_block([Statement_return(Expression_variable("value"))]),
    )
    function_stmt.run(memory)

    expr = Expression_call("identity", [Expression_number(11)])
    value = expr.run(memory)

    assert value == 11
    assert expr.data_type == DataType.INT


def test_expression_call_rejects_wrong_argument_count():
    memory = fresh_memory()
    function_stmt = Statement_function(
        "identity",
        ["value"],
        Statement_block([Statement_return(Expression_variable("value"))]),
    )
    function_stmt.run(memory)

    expr = Expression_call("identity", [])
    assert_raises(TypeError, "expects 1 arguments", lambda: expr.run(memory))

from conftest import run_program, assert_raises
from components.ast.statement import DataType


def infer(text: str) -> DataType:
    _, _, memory = run_program(text)
    return memory.get_type("result")


def test_int_addition():
    _, _, mem = run_program("result = 3 + 4;")
    assert mem.get("result") == 7
    assert mem.get_type("result") == DataType.INT


def test_int_subtraction():
    _, _, mem = run_program("result = 10 - 3;")
    assert mem.get("result") == 7
    assert mem.get_type("result") == DataType.INT


def test_int_multiplication():
    _, _, mem = run_program("result = 3 * 4;")
    assert mem.get("result") == 12
    assert mem.get_type("result") == DataType.INT


def test_float_addition():
    _, _, mem = run_program("result = 1.5 + 2.5;")
    assert mem.get("result") == 4.0
    assert mem.get_type("result") == DataType.FLOAT


def test_division_int_int_yields_float():
    _, _, mem = run_program("result = 10 / 2;")
    assert mem.get("result") == 5.0
    assert mem.get_type("result") == DataType.FLOAT


def test_division_float_float_yields_float():
    _, _, mem = run_program("result = 7.0 / 2.0;")
    assert mem.get_type("result") == DataType.FLOAT


def test_unary_minus_int():
    _, _, mem = run_program("result = -5;")
    assert mem.get("result") == -5
    assert mem.get_type("result") == DataType.INT


def test_unary_minus_float():
    _, _, mem = run_program("result = -3.14;")
    assert mem.get("result") == -3.14


def test_operator_precedence_mul_before_add():
    _, _, mem = run_program("result = 2 + 3 * 4;")
    assert mem.get("result") == 14


def test_parentheses_override_precedence():
    _, _, mem = run_program("result = (2 + 3) * 4;")
    assert mem.get("result") == 20


def test_comparison_less_than_true():
    _, _, mem = run_program("result = 3 < 5;")
    assert mem.get("result") is True
    assert mem.get_type("result") == DataType.BOOL


def test_comparison_less_than_false():
    _, _, mem = run_program("result = 5 < 3;")
    assert mem.get("result") is False


def test_comparison_equal():
    _, _, mem = run_program("result = 4 == 4;")
    assert mem.get("result") is True


def test_comparison_not_equal():
    _, _, mem = run_program("result = 4 != 5;")
    assert mem.get("result") is True


def test_comparison_greater_equal():
    _, _, mem = run_program("result = 5 >= 5;")
    assert mem.get("result") is True


def test_comparison_less_equal():
    _, _, mem = run_program("result = 3 <= 4;")
    assert mem.get("result") is True


def test_boolean_literal_true():
    _, _, mem = run_program("result = true;")
    assert mem.get("result") is True
    assert mem.get_type("result") == DataType.BOOL


def test_boolean_literal_false():
    _, _, mem = run_program("result = false;")
    assert mem.get("result") is False


def test_string_literal():
    _, _, mem = run_program('result = "hello";')
    assert mem.get("result") == "hello"
    assert mem.get_type("result") == DataType.STRING


def test_arithmetic_type_mismatch_raises():
    assert_raises(TypeError, "mismatch", "result = 1 + 1.5;")


def test_arithmetic_on_string_raises():
    assert_raises(TypeError, "does not support", 'result = "a" + "b";')


def test_arithmetic_on_bool_raises():
    assert_raises(TypeError, "does not support", "result = true + false;")


def test_comparison_type_mismatch_raises():
    assert_raises(TypeError, "mismatch", "result = 1 < 1.5;")


def test_comparison_on_string_raises():
    assert_raises(TypeError, "Cannot compare", 'result = "a" < "b";')


def test_variable_before_assignment_raises():
    assert_raises(NameError, "used before assignment", "result = x;")

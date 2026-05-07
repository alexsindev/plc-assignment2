from conftest import run_program, run_with_checker, assert_raises
from components.ast.statement import DataType


# --- assignment ---

def test_assignment_int():
    _, _, mem = run_program("x = 42;")
    assert mem.get("x") == 42
    assert mem.get_type("x") == DataType.INT


def test_assignment_float():
    _, _, mem = run_program("x = 3.14;")
    assert mem.get("x") == 3.14
    assert mem.get_type("x") == DataType.FLOAT


def test_assignment_bool():
    _, _, mem = run_program("x = true;")
    assert mem.get("x") is True
    assert mem.get_type("x") == DataType.BOOL


def test_assignment_string():
    _, _, mem = run_program('x = "hi";')
    assert mem.get("x") == "hi"
    assert mem.get_type("x") == DataType.STRING


def test_assignment_type_change_raises():
    assert_raises(TypeError, "Cannot assign", "x = 1; x = 1.5;")


def test_assignment_same_type_allowed():
    _, _, mem = run_program("x = 1; x = 99;")
    assert mem.get("x") == 99


# --- print ---

def test_print_int():
    mem = run_with_checker("print(7);")
    assert mem.output == ["7"]


def test_print_float():
    mem = run_with_checker("print(3.14);")
    assert mem.output == ["3.14"]


def test_print_bool():
    mem = run_with_checker("print(true);")
    assert mem.output == ["True"]


def test_print_string():
    mem = run_with_checker('print("hello");')
    assert mem.output == ["hello"]


# --- if / else ---

def test_if_true_branch_executes():
    mem = run_with_checker("x = 1; if (x < 2) { print(x); }")
    assert mem.output == ["1"]


def test_if_false_branch_skipped():
    mem = run_with_checker("x = 5; if (x < 2) { print(x); }")
    assert mem.output == []


def test_if_else_true_branch():
    mem = run_with_checker('x = 1; if (x < 2) { print("yes"); } else { print("no"); }')
    assert mem.output == ["yes"]


def test_if_else_false_branch():
    mem = run_with_checker('x = 5; if (x < 2) { print("yes"); } else { print("no"); }')
    assert mem.output == ["no"]


def test_if_condition_not_bool_raises():
    assert_raises(TypeError, "bool", "if (1) { print(1); }")


# --- while ---

def test_while_runs_until_condition_false():
    _, _, mem = run_program("x = 0; while (x < 3) { x = x + 1; }")
    assert mem.get("x") == 3


def test_while_accumulates_sum():
    mem = run_with_checker("i = 1; s = 0; while (i < 6) { s = s + i; i = i + 1; } print(s);")
    assert mem.output == ["15"]


def test_while_condition_not_bool_raises():
    assert_raises(TypeError, "bool", "x = 0; while (x) { x = x + 1; }")


# --- function ---

def test_function_registers_and_returns():
    _, _, mem = run_program("func double(n) { return n * 2; } x = double(5);")
    assert mem.get("x") == 10


def test_function_parameter_types_inferred():
    _, _, mem = run_program("func id(v) { return v; } id(3);")
    fn = mem.get_function("id")
    assert fn.function_type.parameter_types == [DataType.INT]
    assert fn.function_type.return_type == DataType.INT


def test_function_arity_mismatch_raises():
    assert_raises(TypeError, "expects", "func f(a, b) { return a; } f(1);")


def test_function_wrong_arg_type_raises():
    assert_raises(TypeError, "inconsistent", "func f(n) { return n; } f(1); f(true);")


def test_function_inconsistent_return_type_raises():
    assert_raises(
        TypeError, "inconsistent",
        'func f(flag) { if (flag) { return 1; } return "oops"; } f(true); f(false);',
    )


def test_undefined_function_raises():
    assert_raises(NameError, "not defined", "foo();")

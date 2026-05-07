"""
Integration tests — full pipeline (lex → parse → type-check → run).

Each section corresponds to a language feature showcased in examples/.
Tests are split into happy path (correct behaviour) and error path
(violations the language is required to reject).
"""
from conftest import run_with_checker, assert_raises
from components.ast.statement import DataType


# ===========================================================================
# Static Type Binding  (examples/06_static_type_binding.plc)
# ===========================================================================

# --- happy path ---

def test_type_binding_int_division_always_yields_float():
    mem = run_with_checker("result = 10 / 2;")
    assert mem.get("result") == 5.0
    assert mem.get_type("result") == DataType.FLOAT


def test_type_binding_inexact_division_also_float():
    mem = run_with_checker("result = 10 / 3;")
    assert mem.get_type("result") == DataType.FLOAT


def test_type_binding_variable_locked_same_type_reassign_ok():
    mem = run_with_checker("x = 100; x = 200;")
    assert mem.get("x") == 200
    assert mem.get_type("x") == DataType.INT


def test_type_binding_all_four_types_coexist():
    mem = run_with_checker('a = 1; b = 1.5; c = true; d = "hi";')
    assert mem.get_type("a") == DataType.INT
    assert mem.get_type("b") == DataType.FLOAT
    assert mem.get_type("c") == DataType.BOOL
    assert mem.get_type("d") == DataType.STRING


def test_type_binding_function_return_type_locked():
    mem = run_with_checker("func double(n) { return n * 2; } a = double(3); b = double(5);")
    assert mem.get("a") == 6
    assert mem.get("b") == 10
    fn = mem.get_function("double")
    assert fn.function_type.return_type == DataType.INT


# --- error path ---

def test_type_binding_rejects_int_to_float_reassign():
    assert_raises(TypeError, "Cannot assign", "x = 5; x = 3.14;")


def test_type_binding_rejects_int_to_string_reassign():
    assert_raises(TypeError, "Cannot assign", 'x = 5; x = "hello";')


def test_type_binding_rejects_mixed_int_float_arithmetic():
    assert_raises(TypeError, "mismatch", "x = 1 + 1.5;")


def test_type_binding_rejects_string_arithmetic():
    assert_raises(TypeError, "does not support", 'x = "a" + "b";')


def test_type_binding_rejects_bool_arithmetic():
    assert_raises(TypeError, "does not support", "x = true + false;")


def test_type_binding_rejects_string_comparison():
    assert_raises(TypeError, "Cannot compare", 'x = "a" < "b";')


def test_type_binding_rejects_mixed_comparison():
    assert_raises(TypeError, "mismatch", "x = 1 < 1.5;")


def test_type_binding_function_rejects_arg_type_change():
    assert_raises(
        TypeError, "inconsistent",
        "func f(n) { return n; } f(1); f(true);",
    )


# ===========================================================================
# Static Scope Binding  (examples/07_static_scope_binding.plc)
# ===========================================================================

# --- happy path ---

def test_scope_inner_resolves_global_not_caller_local():
    """inner() is defined in global scope; outer() has a local x = 99.
    Lexical scope means inner() sees global x = 1, not outer's x."""
    mem = run_with_checker("""
        x = 1;
        func inner() { print(x); }
        func outer() { x = 99; inner(); }
        outer();
    """)
    assert mem.output == ["1"]


def test_scope_global_unchanged_after_caller_assigns_local():
    mem = run_with_checker("""
        x = 1;
        func outer() { x = 99; return x; }
        y = outer();
    """)
    assert mem.get("x") == 1
    assert mem.get("y") == 99


def test_scope_function_param_does_not_bleed_into_callee():
    """demo(y) receives y=999 locally; getY() resolves y from global frame."""
    mem = run_with_checker("""
        y = 100;
        func getY() { return y; }
        func demo(y) { print(getY()); }
        demo(999);
    """)
    assert mem.output == ["100"]


def test_scope_nested_calls_each_see_own_frame():
    mem = run_with_checker("""
        n = 0;
        func a(n) { return n + 1; }
        func b(n) { return a(n) + 1; }
        result = b(10);
    """)
    assert mem.get("result") == 12
    assert mem.get("n") == 0


# --- error path ---

def test_scope_undefined_variable_raises():
    assert_raises(NameError, "used before assignment", "print(z);")


def test_scope_undefined_function_raises():
    assert_raises(NameError, "not defined", "foo(1);")


def test_scope_variable_used_before_any_assignment_raises():
    assert_raises(NameError, "used before assignment", "x = y + 1;")


# ===========================================================================
# Pass by Value  (examples/08_pass_by_value.plc)
# ===========================================================================

# --- happy path ---

def test_pass_by_value_mutation_does_not_affect_caller():
    mem = run_with_checker("""
        func mutate(n) { n = n + 100; return n; }
        x = 5;
        mutate(x);
    """)
    assert mem.get("x") == 5


def test_pass_by_value_return_carries_new_value():
    mem = run_with_checker("""
        func mutate(n) { n = n + 100; return n; }
        x = 5;
        result = mutate(x);
    """)
    assert mem.get("x") == 5
    assert mem.get("result") == 105


def test_pass_by_value_chained_calls_do_not_affect_original():
    mem = run_with_checker("""
        func addOne(n) { n = n + 1; return n; }
        func addTwo(n) { n = addOne(n); n = addOne(n); return n; }
        a = 10;
        b = addTwo(a);
    """)
    assert mem.get("a") == 10
    assert mem.get("b") == 12


def test_pass_by_value_float_argument_unchanged():
    mem = run_with_checker("""
        func scale(f) { f = f * 2.0; return f; }
        original = 3.5;
        scaled = scale(original);
    """)
    assert mem.get("original") == 3.5
    assert mem.get("scaled") == 7.0


# --- error path ---

def test_pass_by_value_wrong_type_on_second_call_raises():
    assert_raises(
        TypeError, "inconsistent",
        "func f(n) { return n; } f(1); f(true);",
    )


def test_pass_by_value_too_few_args_raises():
    assert_raises(TypeError, "expects", "func f(a, b) { return a; } f(1);")


def test_pass_by_value_too_many_args_raises():
    assert_raises(TypeError, "expects", "func f(a) { return a; } f(1, 2);")


# ===========================================================================
# Functions & Recursion  (examples/05_functions.plc)
# ===========================================================================

# --- happy path ---

def test_function_add():
    mem = run_with_checker("func add(a, b) { return a + b; } result = add(3, 4);")
    assert mem.get("result") == 7


def test_function_max_first_larger():
    mem = run_with_checker("""
        func max(a, b) { if (a > b) { return a; } return b; }
        result = max(10, 20);
    """)
    assert mem.get("result") == 20


def test_function_max_second_larger():
    mem = run_with_checker("""
        func max(a, b) { if (a > b) { return a; } return b; }
        result = max(30, 5);
    """)
    assert mem.get("result") == 30


def test_function_factorial():
    mem = run_with_checker("""
        func factorial(n) {
            if (n < 2) { return 1; }
            return n * factorial(n - 1);
        }
        result = factorial(5);
    """)
    assert mem.get("result") == 120


def test_function_fibonacci():
    mem = run_with_checker("""
        func fib(n) {
            if (n < 2) { return n; }
            return fib(n - 1) + fib(n - 2);
        }
        result = fib(7);
    """)
    assert mem.get("result") == 13


# --- error path ---

def test_function_defined_twice_raises():
    assert_raises(NameError, "already defined", "func f() { return 1; } func f() { return 2; }")


def test_function_inconsistent_return_type_raises():
    assert_raises(
        TypeError, "inconsistent",
        'func f(flag) { if (flag) { return 1; } return "oops"; } f(true); f(false);',
    )


def test_type_error_in_function_body_non_return_statement_caught():
    # Gap 3 fix: assignments inside a function body are type-checked even
    # when they are not on a return path.
    assert_raises(
        TypeError, "mismatch",
        'func broken(n) { x = n + "hello"; return n; } broken(1);',
    )


def test_type_reassign_in_function_body_caught():
    assert_raises(
        TypeError, "Cannot assign",
        'func broken(n) { x = 1; x = 1.5; return n; } broken(1);',
    )


# ===========================================================================
# Control Flow  (examples/03_if_else.plc, 04_while.plc)
# ===========================================================================

# --- happy path ---

def test_if_else_grade_boundary():
    mem = run_with_checker("""
        score = 85;
        if (score > 90) { print("A"); } else { print("B"); }
    """)
    assert mem.output == ["B"]


def test_nested_if_else():
    mem = run_with_checker("""
        score = 75;
        if (score > 90) {
            print("A");
        } else {
            if (score > 80) { print("B"); } else { print("C"); }
        }
    """)
    assert mem.output == ["C"]


def test_while_sum_1_to_5():
    mem = run_with_checker("""
        i = 1; s = 0;
        while (i < 6) { s = s + i; i = i + 1; }
        print(s);
    """)
    assert mem.output == ["15"]


def test_while_doubling_until_limit():
    mem = run_with_checker("""
        n = 1;
        while (n < 100) { n = n * 2; }
        print(n);
    """)
    assert mem.output == ["128"]


# --- error path ---

def test_if_non_bool_condition_raises():
    assert_raises(TypeError, "bool", "if (1) { print(1); }")


def test_if_float_condition_raises():
    assert_raises(TypeError, "bool", "if (1.0) { print(1); }")


def test_while_non_bool_condition_raises():
    assert_raises(TypeError, "bool", "x = 0; while (x) { x = x + 1; }")

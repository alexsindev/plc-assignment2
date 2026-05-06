from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "example"))

from components.ast.expression import DataType
from components.lexica import MyLexer
from components.memory import Memory
from components.parsers import ASTParser


def run_program(text: str):
    memory = Memory()
    memory.reset()
    tree = ASTParser().parse(MyLexer().tokenize(text))
    result = tree.run(memory)
    return tree, result, memory


def assert_program(text: str, expected_output=None, expected_variables=None):
    _, result, memory = run_program(text)
    if expected_output is not None:
        assert memory.output == expected_output
    if expected_variables is not None:
        for name, value in expected_variables.items():
            assert memory.get(name) == value
    return result, memory


def assert_raises(exc_type, expected_message: str, text: str):
    try:
        run_program(text)
    except exc_type as exc:
        assert expected_message in str(exc)
        return exc
    assert False, f"Expected {exc_type.__name__} containing: {expected_message}"


def test_lexer_tokens_cover_statement_keywords():
    lexer = MyLexer()
    tokens = [token.type for token in lexer.tokenize('if (x < 2) { print("ok"); }')]
    assert tokens == [
        "IF",
        "LPAREN",
        "NAME",
        "LESS",
        "NUMBER",
        "RPAREN",
        "LBRACE",
        "PRINT",
        "LPAREN",
        "STRING",
        "RPAREN",
        "SEMI",
        "RBRACE",
    ]


def test_assignment_and_print():
    _, memory = assert_program(
        """
        x = 5;
        print(x);
        """,
        expected_output=["5"],
        expected_variables={"x": 5},
    )
    assert memory.get_type("x") == DataType.INT


def test_expression_types_are_enum_backed():
    tree, _, memory = run_program(
        """
        total = 3.5 + 2.5;
        ok = 2 < 4;
        text = "hello";
        """
    )

    assert memory.get_type("total") == DataType.FLOAT
    assert memory.get_type("ok") == DataType.BOOL
    assert memory.get_type("text") == DataType.STRING
    assert tree.statements[0].expression.data_type == DataType.FLOAT
    assert tree.statements[1].expression.data_type == DataType.BOOL
    assert tree.statements[2].expression.data_type == DataType.STRING


def test_if_else_executes_expected_branch():
    assert_program(
        """
        x = 1;
        if (x < 2) {
            print("small");
        } else {
            print("big");
        }
        """,
        expected_output=["small"],
    )


def test_while_loop_updates_variable():
    _, memory = assert_program(
        """
        x = 0;
        while (x < 3) {
            x = x + 1;
        }
        print(x);
        """,
        expected_output=["3"],
        expected_variables={"x": 3},
    )
    assert memory.get_type("x") == DataType.INT


def test_function_call_and_return():
    _, memory = assert_program(
        """
        func identity(value) {
            return value;
        }
        x = identity(7);
        print(x);
        """,
        expected_output=["7"],
        expected_variables={"x": 7},
    )
    function_stmt = memory.get_function("identity")
    assert function_stmt.function_type.parameter_types == [DataType.INT]
    assert function_stmt.function_type.return_type == DataType.INT


def test_function_uses_static_binding_not_caller_local_scope():
    assert_program(
        """
        x = 1;
        func show() {
            print(x);
        }
        func wrapper() {
            x = 99;
            show();
            return x;
        }
        y = wrapper();
        """,
        expected_output=["1"],
        expected_variables={"x": 1, "y": 99},
    )


def test_if_condition_must_be_boolean():
    assert_raises(
        TypeError,
        "if condition must evaluate to bool",
        """
        if (1) {
            print(1);
        }
        """,
    )


def test_while_condition_must_be_boolean():
    assert_raises(
        TypeError,
        "while condition must evaluate to bool",
        """
        x = 0;
        while (x) {
            x = x + 1;
        }
        """,
    )


def test_assignment_rejects_type_change():
    assert_raises(
        TypeError,
        "Cannot reassign",
        """
        x = 1;
        x = "oops";
        """,
    )


def test_function_signature_is_stable_after_first_call():
    assert_raises(
        TypeError,
        "expects",
        """
        func identity(value) {
            return value;
        }
        identity(1);
        identity(true);
        """,
    )


def test_function_return_type_is_stable_after_first_call():
    assert_raises(
        TypeError,
        "returned",
        """
        func flip(flag) {
            if (flag) {
                return 1;
            }
            return "oops";
        }
        flip(true);
        flip(false);
        """,
    )

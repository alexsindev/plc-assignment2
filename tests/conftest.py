import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "example"))

from components.lexica import MyLexer
from components.memory import Memory
from components.parsers import ASTParser
from components.type_checker import TypeChecker


def parse(text: str):
    return ASTParser().parse(MyLexer().tokenize(text))


def run_program(text: str):
    memory = Memory()
    memory.reset()
    tree = parse(text)
    result = tree.run(memory)
    return tree, result, memory


def run_with_checker(text: str):
    memory = Memory()
    memory.reset()
    tree = parse(text)
    TypeChecker().check(tree)
    tree.run(memory)
    return memory


def assert_output(text: str, expected: list[str]):
    memory = run_with_checker(text)
    assert memory.output == expected


def assert_raises(exc_type, expected_message: str, text: str):
    try:
        run_with_checker(text)
    except exc_type as exc:
        assert expected_message in str(exc), (
            f"Expected message containing {expected_message!r}, got: {exc}"
        )
        return exc
    raise AssertionError(
        f"Expected {exc_type.__name__} containing {expected_message!r} but no exception was raised"
    )

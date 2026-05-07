from __future__ import annotations

from dataclasses import dataclass

from .ast.statement import (
    DataType,
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
    Statement,
    Statement_assignment,
    Statement_block,
    Statement_expression,
    Statement_function,
    Statement_if,
    Statement_print,
    Statement_return,
    Statement_while,
)


@dataclass
class _FuncSig:
    func_stmt: Statement_function
    param_types: list[DataType] | None = None
    return_type: DataType | None = None


class TypeChecker:
    """
    Walks the AST and verifies type correctness before execution.

    Types are inferred from usage — no explicit declarations.
    Variable types are locked at first assignment.
    Function parameter and return types are inferred at the first call site.
    """

    def __init__(self) -> None:
        self._vars: dict[str, DataType] = {}
        self._funcs: dict[str, _FuncSig] = {}
        self._in_progress: set[str] = set()

    def check(self, program: Statement_block) -> None:
        # Pass 1 — register top-level function names so forward calls resolve.
        for stmt in program.statements:
            if isinstance(stmt, Statement_function):
                self._funcs[stmt.function_name] = _FuncSig(func_stmt=stmt)

        # Pass 2 — type-check every statement.
        for stmt in program.statements:
            self._check_stmt(stmt)

    # ------------------------------------------------------------------
    # Expression inference  (returns the DataType of the expression)
    # ------------------------------------------------------------------

    def _infer(self, expr: Expression) -> DataType:
        if isinstance(expr, Expression_number):
            return DataType.INT
        if isinstance(expr, Expression_float):
            return DataType.FLOAT
        if isinstance(expr, Expression_boolean):
            return DataType.BOOL
        if isinstance(expr, Expression_string):
            return DataType.STRING
        if isinstance(expr, Expression_variable):
            if expr.variable_name not in self._vars:
                raise NameError(f"'{expr.variable_name}' used before assignment")
            return self._vars[expr.variable_name]
        if isinstance(expr, Expression_negate):
            t = self._infer(expr.operand)
            if t not in (DataType.INT, DataType.FLOAT):
                raise TypeError(f"Unary minus does not support {t.value}")
            return t
        if isinstance(expr, Expression_math):
            return self._infer_math(expr)
        if isinstance(expr, Expression_compare):
            return self._infer_compare(expr)
        if isinstance(expr, Expression_call):
            return self._infer_call(expr)
        raise NotImplementedError(f"TypeChecker: unhandled expression {type(expr).__name__}")

    def _infer_math(self, expr: Expression_math) -> DataType:
        t1 = self._infer(expr.parameter1)
        t2 = self._infer(expr.parameter2)
        if t1 != t2:
            raise TypeError(f"Type mismatch in arithmetic: {t1.value} and {t2.value}")
        if t1 not in (DataType.INT, DataType.FLOAT):
            raise TypeError(f"Arithmetic does not support {t1.value}")
        return DataType.FLOAT if expr.operation == Operations.DIVIDE else t1

    def _infer_compare(self, expr: Expression_compare) -> DataType:
        t1 = self._infer(expr.parameter1)
        t2 = self._infer(expr.parameter2)
        if t1 != t2:
            raise TypeError(f"Comparison type mismatch: {t1.value} and {t2.value}")
        if t1 not in (DataType.INT, DataType.FLOAT):
            raise TypeError(f"Cannot compare {t1.value} values")
        return DataType.BOOL

    def _infer_call(self, expr: Expression_call) -> DataType:
        name = expr.function_name
        if name not in self._funcs:
            raise NameError(f"Function '{name}' is not defined")

        sig = self._funcs[name]
        arg_types = [self._infer(arg) for arg in expr.arguments]
        expected_arity = len(sig.func_stmt.parameters)

        if len(arg_types) != expected_arity:
            raise TypeError(
                f"'{name}' expects {expected_arity} argument(s), got {len(arg_types)}"
            )

        if sig.param_types is None:
            sig.param_types = arg_types
        elif sig.param_types != arg_types:
            raise TypeError(
                f"'{name}' called with inconsistent argument types: "
                f"expected {[t.value for t in sig.param_types]}, "
                f"got {[t.value for t in arg_types]}"
            )

        # Recursive call — return already-inferred return type to break the cycle.
        if name in self._in_progress:
            return sig.return_type if sig.return_type is not None else DataType.VOID

        # First call — check the body now that param types are known.
        self._check_func_body(sig)
        return sig.return_type if sig.return_type is not None else DataType.VOID

    # ------------------------------------------------------------------
    # Function body checking
    # ------------------------------------------------------------------

    def _check_func_body(self, sig: _FuncSig) -> None:
        name = sig.func_stmt.function_name
        self._in_progress.add(name)

        saved_vars = dict(self._vars)
        for param, ptype in zip(sig.func_stmt.parameters, sig.param_types or []):
            self._vars[param] = ptype

        # Pass 1: collect return types, seeding sig.return_type from the first
        # non-VOID return so recursive calls resolve correctly on the same pass.
        return_types = self._collect_returns(sig.func_stmt.body, sig)

        unique = set(return_types)
        if len(unique) > 1:
            raise TypeError(
                f"Function '{name}' returns inconsistent types: "
                f"{[t.value for t in unique]}"
            )
        sig.return_type = return_types[0] if return_types else DataType.VOID

        # Pass 2: type-check all non-return statements (assignments, print,
        # bare expressions) that _collect_returns skips.
        self._check_block(sig.func_stmt.body)

        self._vars = saved_vars
        self._in_progress.discard(name)

    def _collect_returns(self, block: Statement_block, sig: _FuncSig | None = None) -> list[DataType]:
        result: list[DataType] = []
        for stmt in block.statements:
            result.extend(self._returns_in(stmt, sig))
        return result

    def _returns_in(self, stmt: Statement, sig: _FuncSig | None = None) -> list[DataType]:
        if isinstance(stmt, Statement_return):
            t = self._infer(stmt.expression)
            if sig is not None and sig.return_type is None and t != DataType.VOID:
                sig.return_type = t
            return [t]
        if isinstance(stmt, Statement_if):
            found = self._collect_returns(stmt.then_block, sig)
            if stmt.else_block:
                found += self._collect_returns(stmt.else_block, sig)
            return found
        if isinstance(stmt, Statement_while):
            return self._collect_returns(stmt.body, sig)
        if isinstance(stmt, Statement_block):
            return self._collect_returns(stmt, sig)
        return []

    # ------------------------------------------------------------------
    # Statement checking
    # ------------------------------------------------------------------

    def _check_stmt(self, stmt: Statement) -> None:
        if isinstance(stmt, Statement_assignment):
            t = self._infer(stmt.expression)
            existing = self._vars.get(stmt.variable_name)
            if existing is not None and existing != t:
                raise TypeError(
                    f"Cannot assign {t.value} to '{stmt.variable_name}' "
                    f"(already {existing.value})"
                )
            self._vars[stmt.variable_name] = t

        elif isinstance(stmt, Statement_print):
            self._infer(stmt.expression)

        elif isinstance(stmt, Statement_if):
            t = self._infer(stmt.condition)
            if t != DataType.BOOL:
                raise TypeError(f"if condition must be bool, got {t.value}")
            self._check_block(stmt.then_block)
            if stmt.else_block:
                self._check_block(stmt.else_block)

        elif isinstance(stmt, Statement_while):
            t = self._infer(stmt.condition)
            if t != DataType.BOOL:
                raise TypeError(f"while condition must be bool, got {t.value}")
            self._check_block(stmt.body)

        elif isinstance(stmt, Statement_return):
            self._infer(stmt.expression)

        elif isinstance(stmt, Statement_function):
            if stmt.function_name not in self._funcs:
                self._funcs[stmt.function_name] = _FuncSig(func_stmt=stmt)

        elif isinstance(stmt, Statement_expression):
            self._infer(stmt.expression)

        elif isinstance(stmt, Statement_block):
            self._check_block(stmt)

    def _check_block(self, block: Statement_block) -> None:
        for stmt in block.statements:
            self._check_stmt(stmt)

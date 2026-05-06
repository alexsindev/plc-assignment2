from __future__ import annotations

from abc import ABC, abstractmethod

from ..memory import Memory
from .expression import DataType, Expression, FunctionType


class ReturnSignal(Exception):
    def __init__(self, value: object, data_type: DataType):
        self.value = value
        self.data_type = data_type
        super().__init__("return")


class Statement(ABC):
    @abstractmethod
    def run(self, memory: Memory | None = None) -> object:
        raise NotImplementedError


class Statement_expression(Statement):
    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def run(self, memory: Memory | None = None) -> object:
        mem = memory or Memory()
        return self.expression.run(mem)

    def __repr__(self) -> str:
        return f"Statement_expression({self.expression!r})"


class Statement_assignment(Statement):
    def __init__(self, variable_name: str, expression: Expression) -> None:
        self.variable_name = variable_name
        self.expression = expression

    def run(self, memory: Memory | None = None) -> object:
        mem = memory or Memory()
        value = self.expression.run(mem)
        if self.expression.data_type is None:
            raise TypeError("Assignment expression did not produce a type")
        mem.set(self.variable_name, value, self.expression.data_type)
        return value

    def __repr__(self) -> str:
        return f"Statement_assignment({self.variable_name})"


class Statement_print(Statement):
    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def run(self, memory: Memory | None = None) -> object:
        mem = memory or Memory()
        value = self.expression.run(mem)
        if self.expression.data_type not in [
            DataType.INT,
            DataType.FLOAT,
            DataType.BOOL,
            DataType.STRING,
        ]:
            raise TypeError("print() only supports int, float, bool, and string values")
        mem.write_output(value)
        return value

    def __repr__(self) -> str:
        return f"Statement_print({self.expression!r})"


class Statement_block(Statement):
    def __init__(self, statements: list[Statement] | None = None) -> None:
        self.statements = statements or []

    def run(self, memory: Memory | None = None) -> object:
        mem = memory or Memory()
        last_result = None
        for statement in self.statements:
            last_result = statement.run(mem)
        return last_result

    def __repr__(self) -> str:
        return f"Statement_block(size={len(self.statements)})"


class Statement_if(Statement):
    def __init__(
        self,
        condition: Expression,
        then_block: Statement_block,
        else_block: Statement_block | None = None,
    ) -> None:
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def run(self, memory: Memory | None = None) -> object:
        mem = memory or Memory()
        self.condition.run(mem)
        if self.condition.data_type != DataType.BOOL:
            raise TypeError("if condition must evaluate to bool")

        if self.condition.value:
            return self.then_block.run(mem)
        if self.else_block is not None:
            return self.else_block.run(mem)
        return None

    def __repr__(self) -> str:
        return "Statement_if"


class Statement_while(Statement):
    def __init__(self, condition: Expression, body: Statement_block) -> None:
        self.condition = condition
        self.body = body

    def run(self, memory: Memory | None = None) -> object:
        mem = memory or Memory()
        last_result = None
        while True:
            self.condition.run(mem)
            if self.condition.data_type != DataType.BOOL:
                raise TypeError("while condition must evaluate to bool")
            if not self.condition.value:
                break
            last_result = self.body.run(mem)
        return last_result

    def __repr__(self) -> str:
        return "Statement_while"


class Statement_return(Statement):
    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def run(self, memory: Memory | None = None) -> object:
        mem = memory or Memory()
        value = self.expression.run(mem)
        if self.expression.data_type is None:
            raise TypeError("return expression did not produce a type")
        raise ReturnSignal(value, self.expression.data_type)

    def __repr__(self) -> str:
        return "Statement_return"


class Statement_function(Statement):
    def __init__(self, function_name: str, parameters: list[str], body: Statement_block) -> None:
        self.function_name = function_name
        self.parameters = parameters
        self.body = body
        self.function_type = FunctionType(parameter_types=[], return_type=None)

    def run(self, memory: Memory | None = None) -> object:
        mem = memory or Memory()
        if not mem.is_global_scope():
            raise SyntaxError("Functions can only be defined in the global scope")
        mem.define_function(self.function_name, self)
        return None

    def invoke(
        self,
        argument_values: list[object],
        argument_types: list[DataType],
        memory: Memory | None = None,
    ) -> tuple[object, DataType]:
        mem = memory or Memory()
        if len(argument_values) != len(self.parameters):
            raise TypeError(
                f"Function '{self.function_name}' expects {len(self.parameters)} arguments, "
                f"got {len(argument_values)}"
            )

        if self.function_type.parameter_types:
            assert len(self.function_type.parameter_types) == len(argument_types)
            if self.function_type.parameter_types != argument_types:
                raise TypeError(
                    f"Function '{self.function_name}' expects "
                    f"{self.function_type.parameter_types}, got {argument_types}"
                )
        else:
            self.function_type.parameter_types = list(argument_types)

        mem.push_frame()
        try:
            for name, value, data_type in zip(self.parameters, argument_values, argument_types):
                mem.set(name, value, data_type)

            return_value = None
            return_type = DataType.VOID
            try:
                self.body.run(mem)
            except ReturnSignal as signal:
                return_value = signal.value
                return_type = signal.data_type
        finally:
            mem.pop_frame()

        if self.function_type.return_type is None:
            self.function_type.return_type = return_type
        elif self.function_type.return_type != return_type:
            raise TypeError(
                f"Function '{self.function_name}' returned {return_type}, "
                f"expected {self.function_type.return_type}"
            )

        return return_value, return_type

    def __repr__(self) -> str:
        signature = ", ".join(parameter.value for parameter in self.function_type.parameter_types)
        return_type = (
            self.function_type.return_type.value
            if self.function_type.return_type is not None
            else "unknown"
        )
        return f"Statement_function({self.function_name}({signature}) -> {return_type})"

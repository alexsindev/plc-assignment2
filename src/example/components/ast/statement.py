from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from ..memory import Memory


class DataType(Enum):
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "string"
    VOID = "void"


class Operations(Enum):
    PLUS = 0
    MINUS = 1
    TIMES = 2
    DIVIDE = 3


class CompareOperations(Enum):
    LESS = 0
    GREATER = 1
    EQUAL = 2
    NOT_EQUAL = 3
    LESS_EQUAL = 4
    GREATER_EQUAL = 5


@dataclass
class FunctionType:
    parameter_types: list[DataType]
    return_type: DataType | None = None


class ReturnSignal(Exception):
    def __init__(self, value: object, data_type: DataType):
        self.value = value
        self.data_type = data_type
        super().__init__("return")


class Statement(ABC):
    @abstractmethod
    def run(self, memory: Memory | None = None) -> object:
        raise NotImplementedError


class Expression(ABC):
    def __init__(self) -> None:
        self.signature = ""
        self.value = None
        self.data_type: DataType | None = None

    @abstractmethod
    def run(self, memory: Memory | None = None) -> object:
        raise NotImplementedError


class Expression_math(Expression):
    def __init__(self, operation: Operations, parameter1: Expression, parameter2: Expression):
        super().__init__()
        if not isinstance(operation, Operations):
            raise TypeError("Invalid arithmetic operation")
        self.operation = operation
        self.parameter1 = parameter1
        self.parameter2 = parameter2
        self.children = [self.parameter1, self.parameter2]

    def run(self, memory: Memory | None = None) -> object:
        for child in self.children:
            child.run(memory)

        if self.parameter1.data_type != self.parameter2.data_type:
            raise TypeError(
                f"Type mismatch: {self.parameter1.data_type} and {self.parameter2.data_type}"
            )

        if self.parameter1.data_type not in [DataType.INT, DataType.FLOAT]:
            raise TypeError("Arithmetic operations only support int and float")

        if self.operation == Operations.PLUS:
            self.value = self.parameter1.value + self.parameter2.value
            self.data_type = self.parameter1.data_type
        elif self.operation == Operations.MINUS:
            self.value = self.parameter1.value - self.parameter2.value
            self.data_type = self.parameter1.data_type
        elif self.operation == Operations.TIMES:
            self.value = self.parameter1.value * self.parameter2.value
            self.data_type = self.parameter1.data_type
        elif self.operation == Operations.DIVIDE:
            self.value = self.parameter1.value / self.parameter2.value
            self.data_type = DataType.FLOAT
        else:
            raise ValueError(f"Unsupported arithmetic operation: {self.operation}")

        self.signature = (
            f"Expression_math({self.operation.name}, "
            f"{self.parameter1.value}, {self.parameter2.value})"
        )
        return self.value

    def __repr__(self) -> str:
        return self.signature or f"Expression_math:{self.operation.name}"


class Expression_number(Expression):
    def __init__(self, number: int) -> None:
        super().__init__()
        self.value = number
        self.data_type = DataType.INT
        self.signature = str(number)

    def run(self, memory: Memory | None = None) -> object:
        return self.value

    def __repr__(self) -> str:
        return f"Expression_number:{self.signature}"


class Expression_float(Expression):
    def __init__(self, number: float) -> None:
        super().__init__()
        self.value = number
        self.data_type = DataType.FLOAT
        self.signature = str(number)

    def run(self, memory: Memory | None = None) -> object:
        return self.value

    def __repr__(self) -> str:
        return f"Expression_float:{self.signature}"


class Expression_boolean(Expression):
    def __init__(self, value: bool) -> None:
        super().__init__()
        self.value = value
        self.data_type = DataType.BOOL
        self.signature = str(value)

    def run(self, memory: Memory | None = None) -> object:
        return self.value

    def __repr__(self) -> str:
        return f"Expression_boolean:{self.signature}"


class Expression_string(Expression):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.value = text
        self.data_type = DataType.STRING
        self.signature = text

    def run(self, memory: Memory | None = None) -> object:
        return self.value

    def __repr__(self) -> str:
        return f'Expression_string:"{self.signature}"'


class Expression_variable(Expression):
    def __init__(self, variable_name: str) -> None:
        super().__init__()
        self.variable_name = variable_name

    def run(self, memory: Memory | None = None) -> object:
        mem = memory or Memory()
        self.value = mem.get(self.variable_name)
        self.data_type = mem.get_type(self.variable_name)
        return self.value

    def __repr__(self) -> str:
        return f"Expression_variable:{self.variable_name}"


class Expression_call(Expression):
    def __init__(self, function_name: str, arguments: list[Expression]) -> None:
        super().__init__()
        self.function_name = function_name
        self.arguments = arguments

    def run(self, memory: Memory | None = None) -> object:
        mem = memory or Memory()
        function_stmt = mem.get_function(self.function_name)

        argument_values = []
        argument_types = []
        for argument in self.arguments:
            argument.run(mem)
            argument_values.append(argument.value)
            argument_types.append(argument.data_type)

        self.value, self.data_type = function_stmt.invoke(argument_values, argument_types, mem)
        return self.value

    def __repr__(self) -> str:
        return f"Expression_call:{self.function_name}"


class Expression_compare(Expression):
    def __init__(
        self,
        operation: CompareOperations,
        parameter1: Expression,
        parameter2: Expression,
    ) -> None:
        super().__init__()
        if not isinstance(operation, CompareOperations):
            raise TypeError("Invalid comparison operation")
        self.operation = operation
        self.parameter1 = parameter1
        self.parameter2 = parameter2
        self.children = [self.parameter1, self.parameter2]
        self.data_type = DataType.BOOL

    def run(self, memory: Memory | None = None) -> object:
        for child in self.children:
            child.run(memory)

        if self.parameter1.data_type != self.parameter2.data_type:
            raise TypeError("Comparison type mismatch")

        if self.parameter1.data_type not in [DataType.INT, DataType.FLOAT]:
            raise TypeError("Comparisons only support int and float operands")

        left = self.parameter1.value
        right = self.parameter2.value

        if self.operation == CompareOperations.LESS:
            self.value = left < right
        elif self.operation == CompareOperations.GREATER:
            self.value = left > right
        elif self.operation == CompareOperations.EQUAL:
            self.value = left == right
        elif self.operation == CompareOperations.NOT_EQUAL:
            self.value = left != right
        elif self.operation == CompareOperations.LESS_EQUAL:
            self.value = left <= right
        elif self.operation == CompareOperations.GREATER_EQUAL:
            self.value = left >= right
        else:
            raise ValueError("Unsupported comparison operator")

        return self.value

    def __repr__(self) -> str:
        return f"Expression_compare:{self.operation.name}"


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

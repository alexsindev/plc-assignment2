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

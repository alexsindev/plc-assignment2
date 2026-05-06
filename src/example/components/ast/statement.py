from enum import Enum
from abc import ABC, abstractmethod
from ..memory import Memory

class Statement:
    """What is statement?
    In this calculator project, a statement is each line of math expression.
    In this case, it will consit of tree of math expression
    """
    def __init__(self) -> None:
        self.root_node = None

class DataType(Enum):
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "string"      

class Operations(Enum):
    PLUS:int=0
    MINUS:int=1
    TIMES:int=2
    DIVIDE:int=3

class Expression(ABC): 
    @abstractmethod
    def __init__(self) -> None:
        self.signature:str = ""
        self.value = None
        self.data_type = None
        pass

    @abstractmethod
    def run(self) -> None:
        pass

class Expression_math(Expression):
    def __init__(self, operation:Operations, parameter1:Expression, parameter2:Expression):
        # Init attribute
        self.operation:Operations = operation
        self.parameter1:Expression = parameter1
        self.parameter2:Expression = parameter2
        self.signature:str = ""
        self.value = None
        # Checking Logic
        if not isinstance(operation, Operations):
            raise TypeError("Invalid arithmetic operation")

        # Create a children
        self.children = [self.parameter1, self.parameter2]
        
    def run(self) -> None:
        # evaluate child first
        for child in self.children:
            child.run()
            # print(child)
        if self.parameter1.data_type != self.parameter2.data_type:
            raise TypeError(
                f"Type mismatch: "
                f"{self.parameter1.data_type} "
                f"and "
                f"{self.parameter2.data_type}"
            )
        allowed_types = [DataType.INT, DataType.FLOAT]

        if self.parameter1.data_type not in allowed_types:
            raise TypeError(
                "Arithmetic operations only support int and float"
            )
        if(self.operation == Operations.PLUS):
            self.value = self.parameter1.value + self.parameter2.value
        elif(self.operation == Operations.MINUS):
            self.value = self.parameter1.value - self.parameter2.value
        elif(self.operation == Operations.TIMES):
            self.value = self.parameter1.value * self.parameter2.value
        elif(self.operation == Operations.DIVIDE):
            self.value = self.parameter1.value / self.parameter2.value
        else:
            raise ValueError(f"{self.operation=} is not support. Please use class Statement.Operations. Actually, this should not happen.")
        
        self.data_type = self.parameter1.data_type

        self.signature = f"Expression: {self.operation.name} {self.parameter1.value} {self.parameter2.value}"
        print(self)

    def __repr__(self) -> str:
        return self.signature

class Expression_number(Expression):
    def __init__(self, number:int) -> None:
        self.value = number
        self.data_type = DataType.INT
        self.signature:str= str(number)
        
    def run(self) -> None:
        print(self)

    def __repr__(self) -> str:
        return f"Expression_number:{self.signature}"
    
class Expression_float(Expression):
    def __init__(self, number: float):
        self.value = number
        self.data_type = DataType.FLOAT
        self.signature = str(number)

    def run(self):
        print(self)

    def __repr__(self):
        return f"Expression_float:{self.signature}"
    
class Expression_boolean(Expression):
    def __init__(self, value: bool):
        self.value = value
        self.data_type = DataType.BOOL
        self.signature = str(value)

    def run(self):
        print(self)

    def __repr__(self):
        return f"Expression_boolean:{self.signature}"
    
class Expression_string(Expression):
    def __init__(self, text: str):
        self.value = text
        self.data_type = DataType.STRING
        self.signature = text

    def run(self):
        print(self)

    def __repr__(self):
        return f'Expression_string:"{self.signature}"'
    
class Expression_variable(Expression):
    def __init__(self, variable_name: str):
        self.variable_name = variable_name
        self.value = None
        self.data_type = None

    def run(self):
        memory = Memory()
        if self.variable_name not in memory.variables:
            raise NameError(
                f"Variable '{self.variable_name}' is not defined"
            )
        variable_data = memory.variables[self.variable_name]

        self.value = variable_data["value"]
        self.data_type = variable_data["data_type"]

    def __repr__(self):
        return f"Expression_variable:{self.variable_name}"
    
class CompareOperations(Enum):
    LESS = 0
    GREATER = 1
    EQUAL = 2
    NOT_EQUAL = 3
    LESS_EQUAL = 4
    GREATER_EQUAL = 5

class Expression_compare(Expression):

    def __init__( self, operation: CompareOperations, parameter1: Expression,parameter2: Expression):
        self.operation = operation
        self.parameter1 = parameter1
        self.parameter2 = parameter2

        self.value = None
        self.data_type = DataType.BOOL

        self.children = [parameter1, parameter2]

        if not isinstance(operation, CompareOperations):
            raise TypeError("Invalid comparison operation")

    def run(self):

        for child in self.children:
            child.run()

        left = self.parameter1.value
        right = self.parameter2.value

        if self.parameter1.data_type != self.parameter2.data_type:
            raise TypeError("Comparison type mismatch")

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

    def __repr__(self):
        return f"Expression_compare:{self.operation.name}"

if __name__ == "__main__":
    number1 = Expression_number(number=8)
    number2 = Expression_number(number=9)
    expr = Expression_math(Operations.MINUS, parameter1=number1, parameter2=number2)
    expr.run()
    # print(expr.hshow())
    print(expr.value)
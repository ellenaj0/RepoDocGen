"""
Main calculator module with basic and advanced operations
"""

from typing import List
from utils import validate_number


class Calculator:
    """A simple calculator with history tracking"""

    def __init__(self):
        """Initialize calculator with empty history"""
        self.history: List[str] = []

    def add(self, a: float, b: float) -> float:
        """Add two numbers together"""
        validate_number(a)
        validate_number(b)
        result = a + b
        self._add_to_history(f"{a} + {b} = {result}")
        return result

    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a"""
        validate_number(a)
        validate_number(b)
        result = a - b
        self._add_to_history(f"{a} - {b} = {result}")
        return result

    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers"""
        validate_number(a)
        validate_number(b)
        result = a * b
        self._add_to_history(f"{a} x {b} = {result}")
        return result

    def divide(self, a: float, b: float) -> float:
        """Divide a by b"""
        validate_number(a)
        validate_number(b)
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self._add_to_history(f"{a} ÷ {b} = {result}")
        return result

    def power(self, base: float, exponent: float) -> float:
        """Raise base to the power of exponent"""
        validate_number(base)
        validate_number(exponent)
        result = base ** exponent
        self._add_to_history(f"{base} ^ {exponent} = {result}")
        return result

    def get_history(self) -> List[str]:
        """Get calculation history"""
        return self.history.copy()

    def clear_history(self):
        """Clear calculation history"""
        self.history.clear()

    def _add_to_history(self, operation: str):
        """Add operation to history"""
        self.history.append(operation)


class ScientificCalculator(Calculator):
    """Extended calculator with scientific functions"""

    def square_root(self, n: float) -> float:
        """Calculate square root of n"""
        validate_number(n)
        if n < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = n ** 0.5
        self._add_to_history(f"√{n} = {result}")
        return result

    def factorial(self, n: int) -> int:
        """Calculate factorial of n"""
        if not isinstance(n, int) or n < 0:
            raise ValueError("Factorial requires non-negative integer")
        if n == 0 or n == 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        self._add_to_history(f"{n}! = {result}")
        return result

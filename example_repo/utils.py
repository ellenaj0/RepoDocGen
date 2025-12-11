"""
Utility functions for calculator operations
"""

from typing import Union


def validate_number(value: Union[int, float]) -> None:
    """
    Validate that value is a number

    Args:
        value: The value to validate

    Raises:
        TypeError: If value is not a number
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"Expected number, got {type(value).__name__}")


def format_result(value: float, precision: int = 2) -> str:
    """
    Format a number for display

    Args:
        value: The number to format
        precision: Number of decimal places

    Returns:
        Formatted string representation
    """
    return f"{value:.{precision}f}"


def is_even(n: int) -> bool:
    """Check if a number is even"""
    return n % 2 == 0


def is_odd(n: int) -> bool:
    """Check if a number is odd"""
    return n % 2 != 0


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between min and max

    Args:
        value: The value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))

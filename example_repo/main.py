"""
Main entry point for calculator demo
"""

from calculator import Calculator, ScientificCalculator


def demo_basic_operations():
    """Demonstrate basic calculator operations"""
    print("=== Basic Calculator Demo ===")
    calc = Calculator()

    # Basic operations
    print(f"5 + 3 = {calc.add(5, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
    print(f"6 x 7 = {calc.multiply(6, 7)}")
    print(f"20 ÷ 4 = {calc.divide(20, 4)}")

    # Show history
    print("\nCalculation History:")
    for entry in calc.get_history():
        print(f"  {entry}")


def demo_scientific_operations():
    """Demonstrate scientific calculator operations"""
    print("\n=== Scientific Calculator Demo ===")
    sci_calc = ScientificCalculator()

    # Scientific operations
    print(f"2 ^ 8 = {sci_calc.power(2, 8)}")
    print(f"√16 = {sci_calc.square_root(16)}")
    print(f"5! = {sci_calc.factorial(5)}")

    # Show history
    print("\nCalculation History:")
    for entry in sci_calc.get_history():
        print(f"  {entry}")


def main():
    """Run calculator demonstrations"""
    demo_basic_operations()
    demo_scientific_operations()
    print("\n✓ Demo complete!")


if __name__ == "__main__":
    main()

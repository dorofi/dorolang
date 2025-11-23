#!/usr/bin/env python3
"""
DoroLang - Main Module
Entry point for the DoroLang language interpreter

Usage:
    python main.py                    # Examples
    python main.py interactive        # Interactive mode
    python main.py examples           # All examples
    python main.py test              # Testing
    python main.py program.doro       # Run file

Author: Dorofii Karnaukh
"""

import sys
import os
from typing import List, Optional

# Import our modules
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, RuntimeError as DoroRuntimeError


class DoroLang:
    """
    Main DoroLang interpreter class
    
    Coordinates the work of lexer, parser, and interpreter
    """
    
    def __init__(self):
        self.lexer: Optional[Lexer] = None
        self.parser: Optional[Parser] = None
        self.interpreter = Interpreter()
        self.version = "1.1.0"
    
    def run(self, source_code: str, show_details: bool = False) -> List[str]:
        """
        Executes DoroLang code
        
        Args:
            source_code: Source code of the program
            show_details: Whether to show execution details
            
        Returns:
            List[str]: Program output
        """
        try:
            # Lexical analysis
            if show_details:
                print("🔍 Lexical Analysis...")
            
            self.lexer = Lexer(source_code)
            tokens = self.lexer.tokenize()
            
            if show_details:
                print(f"   Found {len(tokens)} tokens")
                # Show first few tokens
                for i, token in enumerate(tokens[:5]):
                    if token.type.name != 'EOF':
                        print(f"     {i}: {token.type.name} '{token.value}'")
                if len(tokens) > 6:
                    print(f"     ... and {len(tokens) - 5} more tokens")
            
            # Syntax analysis
            if show_details:
                print("🌳 Parsing...")
            
            self.parser = Parser(tokens)
            ast = self.parser.parse()
            
            if show_details:
                print(f"   Built AST with {len(ast.statements)} statements")
            
            # Interpretation
            if show_details:
                print("🚀 Executing...")
                print("-" * 30)
            
            output = self.interpreter.interpret(ast)
            
            if show_details:
                print("-" * 30)
                print("✅ Execution completed!")
                
                # Show variables if any
                variables = self.interpreter.get_variables()
                if variables:
                    print("\n📊 Final variables:")
                    for name, value in variables.items():
                        print(f"   {name} = {value} ({type(value).__name__})")
            
            return output
            
        except LexerError as e:
            error_msg = f"❌ Lexer error: {e}"
            print(error_msg)
            return [error_msg]
            
        except ParseError as e:
            error_msg = f"❌ Parse error: {e}"
            print(error_msg)
            return [error_msg]
            
        except DoroRuntimeError as e:
            error_msg = f"❌ Runtime error: {e}"
            print(error_msg)
            return [error_msg]
            
        except Exception as e:
            error_msg = f"❌ Unexpected error: {e}"
            print(error_msg)
            return [error_msg]
    
    def run_interactive(self) -> None:
        """
        Interactive mode (REPL - Read-Eval-Print Loop)
        """
        print("=" * 60)
        print(f"🎉 DoroLang Interactive Mode v{self.version}")
        print("   Created by Dorofii Karnaukh")
        print("-" * 60)
        print("Commands:")
        print("  Type DoroLang code and press Enter to execute")
        print("  'exit' or 'quit' - exit")
        print("  'vars' - show variables")
        print("  'clear' - clear variables")
        print("  'help' - show this help")
        print("=" * 60)
        
        while True:
            try:
                line = input("DoroLang> ").strip()
                
                # Commands
                if line.lower() in ['exit', 'quit']:
                    print("👋 Goodbye!")
                    break
                    
                elif line.lower() == 'vars':
                    variables = self.interpreter.get_variables()
                    if variables:
                        print("📊 Variables:")
                        for name, value in variables.items():
                            print(f"   {name} = {value} ({type(value).__name__})")
                    else:
                        print("📊 No variables defined")
                    continue
                    
                elif line.lower() == 'clear':
                    self.interpreter.reset()
                    print("🧹 Variables cleared")
                    continue
                    
                elif line.lower() == 'help':
                    print("DoroLang syntax:")
                    print("  say \"text\"        - print text")
                    print("  kas var = value    - assign variable")
                    print("  if (condition) { } - conditional")
                    print("  true, false        - boolean values")
                    print("  and, or, not       - logical operators")
                    print("  Operators: +, -, *, /, %")
                    print("  Comparison: ==, !=, <, >, <=, >=")
                    print("  Parentheses: (expression)")
                    print("  Unary: -x, +x, not x")
                    continue
                    
                elif not line:
                    continue
                
                # Execute code
                self.run(line, show_details=False)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
    
    def run_file(self, filepath: str) -> None:
        """
        Runs a DoroLang file
        
        Args:
            filepath: Path to the file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            print(f"🚀 Running file: {filepath}")
            print("-" * 50)
            
            self.run(code, show_details=True)
            
        except FileNotFoundError:
            print(f"❌ File not found: {filepath}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")


def run_examples() -> None:
    """Demonstrates DoroLang capabilities"""
    
    examples = [
        ("Hello World", '''
say "Hello, DoroLang!"
say "Created by Dorofii Karnaukh"
        '''),
        
        ("Variables and Arithmetic", '''
kas name = "DoroLang"
kas version = 1.1
say "Language: " + name
say "Version: " + version

kas a = 10
kas b = 3
say "a = " + a + ", b = " + b
say "a + b = " + (a + b)
say "a - b = " + (a - b)
say "a * b = " + (a * b)
say "a / b = " + (a / b)
say "a % b = " + (a % b)
        '''),
        
        ("Boolean Values and Logic", '''
kas is_sunny = true
kas is_weekend = false
kas temperature = 25

say "Is sunny: " + is_sunny
say "Is weekend: " + is_weekend
say "Temperature: " + temperature

# Логические операции
kas good_weather = is_sunny and temperature > 20
kas can_relax = is_weekend or good_weather
kas stay_inside = not (good_weather and is_weekend)

say "Good weather: " + good_weather
say "Can relax: " + can_relax
say "Stay inside: " + stay_inside
        '''),
        
        ("Conditional Statements", '''
kas age = 25
kas has_license = true

say "Age: " + age
say "Has license: " + has_license

if (age >= 18 and has_license) {
    say "Can drive a car!"
    kas status = "eligible"
} else {
    say "Cannot drive yet"
    kas status = "not eligible"  
}

# Вложенные условия
if (age >= 65) {
    say "Senior citizen discount available"
} else {
    if (age >= 18) {
        say "Regular adult pricing"
    } else {
        say "Child discount available"
    }
}
        '''),
        
        ("Complex Logic", '''
kas score = 85
kas attendance = 90
kas has_extra_credit = true

say "Score: " + score
say "Attendance: " + attendance + "%"
say "Extra credit: " + has_extra_credit

# Сложное условие для оценки
kas excellent = score >= 90 and attendance >= 85
kas good = (score >= 80 and attendance >= 80) or has_extra_credit
kas needs_improvement = not (good or excellent)

if (excellent) {
    say "Grade: A - Excellent work!"
} else {
    if (good) {
        say "Grade: B - Good job!"
    } else {
        say "Grade: C - Needs improvement"
    }
}
        '''),
        
        ("String Operations", '''
kas first_name = "Dorofii"
kas last_name = "Karnaukh"
kas full_name = first_name + " " + last_name

say "First name: " + first_name
say "Last name: " + last_name  
say "Full name: " + full_name

kas age = 25
kas is_student = true
kas message = full_name + " is " + age + " years old"

if (is_student) {
    kas student_info = message + " and is a student"
    say student_info
} else {
    say message + " and is not a student"
}
        '''),
        
        ("Advanced Expressions", '''
kas x = 5
kas y = 3
kas z = 2
kas flag = true

say "Variables: x=" + x + ", y=" + y + ", z=" + z + ", flag=" + flag

# Сложные арифметические выражения
kas result1 = -(x + y) * z % (x - y)
kas result2 = -((x + y) * z) + (x % y)

say "-(x + y) * z % (x - y) = " + result1
say "-((x + y) * z) + (x % y) = " + result2

# Сложные логические выражения  
kas complex_logic = (x > y or flag) and not (z == 0) or (x + y) >= 8
say "Complex logic result: " + complex_logic

# Комбинированные условия
if ((x + y + z) > 9 and flag) or (x * y) > 10) {
    say "Complex condition met!"
    kas final_result = "success"
} else {
    say "Complex condition not met"
    kas final_result = "failure"
}

say "Final result: " + final_result
        '''),
        
        ("Type Coercion Demo", '''
kas number = 42
kas text = "The answer is: "
kas is_correct = true
kas zero = 0
kas empty = ""

say "Demonstrating type coercion:"
say text + number
say "Is correct: " + is_correct
say "Number + boolean: " + (number + is_correct)

# Демонстрация истинности
say "Truthiness demo:"
say "42 is truthy: " + (not not number)
say "0 is truthy: " + (not not zero) 
say "true is truthy: " + (not not is_correct)
say "Empty string is truthy: " + (not not empty)
say "Non-empty string is truthy: " + (not not text)

if (number and text and is_correct) {
    say "All values are truthy!"
}

if (not zero and not empty) {
    say "Zero and empty string are falsy!"
}
        ''')
    ]
    
    dorolang = DoroLang()
    
    for title, code in examples:
        print("\n" + "=" * 70)
        print(f"📝 Example: {title}")
        print("=" * 70)
        print("Source code:")
        print(code.strip())
        print(f"\n🚀 Output:")
        print("-" * 40)
        
        # Reset variables for each example
        dorolang.interpreter.reset()
        dorolang.run(code.strip(), show_details=False)
        
        print("-" * 40)


def show_usage() -> None:
    """Shows usage help"""
    print(f"DoroLang Programming Language Interpreter v1.1.0")
    print("Created by Dorofii Karnaukh")
    print()
    print("Usage:")
    print("  python main.py                    # Run examples")
    print("  python main.py interactive        # Interactive mode (REPL)")
    print("  python main.py examples           # Show all examples")
    print("  python main.py test              # Run tests")
    print("  python main.py <file.doro>        # Execute DoroLang file")
    print()
    print("DoroLang Features:")
    print("  ✅ Variables (kas x = value)")
    print("  ✅ Print statements (say expression)")
    print("  ✅ Arithmetic (+, -, *, /, %)")
    print("  ✅ Comparison (==, !=, <, >, <=, >=)")
    print("  ✅ Logical operators (and, or, not)")
    print("  ✅ Boolean values (true, false)")
    print("  ✅ Conditional statements (if/else)")
    print("  ✅ Block statements ({ ... })")
    print("  ✅ Unary operations (-x, +x, not x)")
    print("  ✅ Parentheses for precedence")
    print("  ✅ String concatenation")
    print("  ✅ Type coercion")
    print("  ✅ Comments (# comment)")


def run_tests() -> None:
    """Runs extended DoroLang tests"""
    print("🧪 Running Enhanced DoroLang tests...")
    print("=" * 50)
    
    dorolang = DoroLang()
    
    tests = [
        ("Basic arithmetic", 'kas x = 2 + 3 * 4\nsay x'),
        ("Parentheses", 'kas x = (2 + 3) * 4\nsay x'),
        ("Unary minus", 'kas x = -5\nsay x'),
        ("Modulo", 'kas x = 17 % 5\nsay x'),
        ("String concat", 'say "Hello, " + "World!"'),
        ("Mixed types", 'say "Result: " + (2 + 3)'),
        ("Complex expression", 'kas x = -(2 + 3) * 4 % 7\nsay x'),
        
        # New tests for logic
        ("Boolean literals", 'kas a = true\nkas b = false\nsay a\nsay b'),
        ("Logical AND", 'kas result = true and false\nsay result'),
        ("Logical OR", 'kas result = true or false\nsay result'),
        ("Logical NOT", 'kas result = not true\nsay result'),
        ("Complex logic", 'kas x = 5 > 3 and 2 < 4\nsay x'),
        
        # Conditional tests
        ("Simple if-true", 'if (true) {\nsay "true branch"\n}'),
        ("Simple if-false", 'if (false) {\nsay "true branch"\n} else {\nsay "false branch"\n}'),
        ("Comparison in if", 'kas x = 10\nif (x > 5) {\nsay "x is big"\n}'),
        ("Complex condition", 'kas x = 5\nkas y = 3\nif (x > y and x < 10) {\nsay "condition met"\n}'),
        
        # Truthiness tests
        ("Zero truthiness", 'if (not 0) {\nsay "zero is falsy"\n}'),
        ("String truthiness", 'if ("hello") {\nsay "string is truthy"\n}'),
        ("Empty string", 'if (not "") {\nsay "empty string is falsy"\n}'),
        
        # Type tests
        ("Boolean to string", 'say "Value: " + true'),
        ("Number comparison", 'say 10 > 5'),
        ("String equality", 'say "hello" == "hello"'),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, code in tests:
        try:
            print(f"\n🧪 Test: {name}")
            print(f"   Code: {code.replace(chr(10), '; ')}")
            
            dorolang.interpreter.reset()
            output = dorolang.run(code, show_details=False)
            
            if output and not any("❌" in line for line in output):
                print(f"   ✅ PASSED")
                passed += 1
            else:
                print(f"   ❌ FAILED")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"❌ {total - passed} tests failed")


def main() -> None:
    """Main function"""
    
    if len(sys.argv) == 1:
        # No arguments - show examples
        print("🎉 DoroLang Programming Language v1.1.0")
        print("   Enhanced with Boolean Logic & Conditionals!")
        run_examples()
        print("\n" + "=" * 70)
        show_usage()
        
    elif len(sys.argv) == 2:
        arg = sys.argv[1].lower()
        
        if arg == "interactive":
            dorolang = DoroLang()
            dorolang.run_interactive()
            
        elif arg == "examples":
            run_examples()
            
        elif arg == "test":
            run_tests()
            
        elif arg in ["help", "--help", "-h"]:
            show_usage()
            
        else:
            # Assume it's a file
            if os.path.exists(sys.argv[1]):
                dorolang = DoroLang()
                dorolang.run_file(sys.argv[1])
            else:
                print(f"❌ File not found: {sys.argv[1]}")
                print("Use 'python main.py help' for usage information")
    else:
        print("❌ Too many arguments")
        show_usage()


if __name__ == "__main__":
    main()
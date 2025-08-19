#!/usr/bin/env python3
"""
DoroLang - Главный модуль
Точка входа в интерпретатор языка DoroLang

Использование:
    python main.py                    # Примеры
    python main.py interactive        # Интерактивный режим
    python main.py examples           # Все примеры
    python main.py test              # Тестирование
    python main.py program.doro       # Запуск файла

Автор: Dorofii Karnaukh
"""

import sys
import os
from typing import List, Optional

# Импортируем наши модули
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, RuntimeError as DoroRuntimeError


class DoroLang:
    """
    Главный класс интерпретатора DoroLang
    
    Координирует работу лексера, парсера и интерпретатора
    """
    
    def __init__(self):
        self.lexer: Optional[Lexer] = None
        self.parser: Optional[Parser] = None
        self.interpreter = Interpreter()
        self.version = "1.0.0"
    
    def run(self, source_code: str, show_details: bool = False) -> List[str]:
        """
        Выполняет код на DoroLang
        
        Args:
            source_code: Исходный код программы
            show_details: Показывать ли подробности выполнения
            
        Returns:
            List[str]: Вывод программы
        """
        try:
            # Лексический анализ
            if show_details:
                print("🔍 Lexical Analysis...")
            
            self.lexer = Lexer(source_code)
            tokens = self.lexer.tokenize()
            
            if show_details:
                print(f"   Found {len(tokens)} tokens")
                # Показываем первые несколько токенов
                for i, token in enumerate(tokens[:5]):
                    if token.type.name != 'EOF':
                        print(f"     {i}: {token.type.name} '{token.value}'")
                if len(tokens) > 6:
                    print(f"     ... и еще {len(tokens) - 5} токенов")
            
            # Синтаксический анализ
            if show_details:
                print("🌳 Parsing...")
            
            self.parser = Parser(tokens)
            ast = self.parser.parse()
            
            if show_details:
                print(f"   Built AST with {len(ast.statements)} statements")
            
            # Интерпретация
            if show_details:
                print("🚀 Executing...")
                print("-" * 30)
            
            output = self.interpreter.interpret(ast)
            
            if show_details:
                print("-" * 30)
                print("✅ Execution completed!")
                
                # Показываем переменные если они есть
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
        Интерактивный режим (REPL - Read-Eval-Print Loop)
        """
        print("=" * 60)
        print(f"🎉 DoroLang Interactive Mode v{self.version}")
        print("   Created by Dorofii Karnaukh")
        print("-" * 60)
        print("Commands:")
        print("  Type DoroLang code and press Enter to execute")
        print("  'exit' or 'quit' - выйти")
        print("  'vars' - показать переменные")
        print("  'clear' - очистить переменные")
        print("  'help' - показать эту справку")
        print("=" * 60)
        
        while True:
            try:
                line = input("DoroLang> ").strip()
                
                # Команды
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
                    print("  Operators: +, -, *, /, %")
                    print("  Parentheses: (expression)")
                    print("  Unary: -x, +x")
                    continue
                    
                elif not line:
                    continue
                
                # Выполняем код
                self.run(line, show_details=False)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
    
    def run_file(self, filepath: str) -> None:
        """
        Запускает файл DoroLang
        
        Args:
            filepath: Путь к файлу
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
    """Демонстрация возможностей DoroLang"""
    
    examples = [
        ("Hello World", '''
say "Hello, DoroLang!"
say "Created by Dorofii Karnaukh"
        '''),
        
        ("Variables and Arithmetic", '''
kas name = "DoroLang"
kas version = 1.0
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
        
        ("Unary Operations", '''
kas positive = 42
kas negative = -positive
kas double_negative = -negative

say "positive = " + positive
say "negative = " + negative
say "double negative = " + double_negative
say "unary plus = " + (+positive)
        '''),
        
        ("Complex Expressions", '''
kas x = 5
kas y = 3
kas z = 2

say "Simple: " + (x + y)
say "With precedence: " + (x + y * z)
say "With parentheses: " + ((x + y) * z)
say "Complex: " + (-(x + y) * z % (x - y))
say "Very complex: " + (-((x + y) * z) + (x % y))
        '''),
        
        ("String Operations", '''
kas first_name = "Dorofii"
kas last_name = "Karnaukh"
kas full_name = first_name + " " + last_name

say "First name: " + first_name
say "Last name: " + last_name  
say "Full name: " + full_name

kas age = 25
say full_name + " is " + age + " years old"
        '''),
        
        ("Mixed Types", '''
kas pi = 3.14159
kas radius = 5
kas area = pi * radius * radius

say "Pi = " + pi
say "Radius = " + radius
say "Area = " + area

kas message = "The area of circle with radius " + radius + " is " + area
say message
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
        
        # Сбрасываем переменные для каждого примера
        dorolang.interpreter.reset()
        dorolang.run(code.strip(), show_details=False)
        
        print("-" * 40)


def show_usage() -> None:
    """Показывает справку по использованию"""
    print(f"DoroLang Programming Language Interpreter")
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
    print("  ✅ Unary operations (-x, +x)")
    print("  ✅ Parentheses for precedence")
    print("  ✅ String concatenation")
    print("  ✅ Mixed type operations")
    print("  ✅ Comments (# comment)")


def run_tests() -> None:
    """Запускает тесты DoroLang"""
    print("🧪 Running DoroLang tests...")
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
    """Главная функция"""
    
    if len(sys.argv) == 1:
        # Без аргументов - показываем примеры
        print("🎉 DoroLang Programming Language")
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
            # Предполагаем что это файл
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
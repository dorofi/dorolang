#!/usr/bin/env python3
"""
DoroLang - Полная реализация языка программирования
Создано: 2025
Автор: Dorofii Karnaukh

Особенности:
- Переменные (let x = 5)
- Print statements
- Арифметические операции (+, -, *, /)
- Строки и числа
- Правильный приоритет операторов
"""

import re
from abc import ABC, abstractmethod
from typing import List, Optional, Union, Any, Dict
from dataclasses import dataclass
from enum import Enum, auto

# ============== LEXER ==============

class TokenType(Enum):
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    PRINT = auto()
    LET = auto()
    ASSIGN = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    NEWLINE = auto()
    EOF = auto()
    UNKNOWN = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
        self.token_patterns = [
            (r'say', TokenType.PRINT),
            (r'kas', TokenType.LET),
            (r'\d+\.?\d*', TokenType.NUMBER),
            (r'"[^"]*"', TokenType.STRING),
            (r"'[^']*'", TokenType.STRING),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
            (r'=', TokenType.ASSIGN),
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'\n', TokenType.NEWLINE),
        ]
    
    def tokenize(self) -> List[Token]:
        tokens = []
        lines = self.source.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            line = line.strip()
            
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('#'):
                continue
            
            pos = 0
            while pos < len(line):
                # Пропускаем пробелы
                if line[pos] in ' \t':
                    pos += 1
                    continue
                
                found_match = False
                remaining = line[pos:]
                
                for pattern, token_type in self.token_patterns:
                    match = re.match(pattern, remaining)
                    if match:
                        value = match.group(0)
                        tokens.append(Token(token_type, value, line_num, pos + 1))
                        pos += len(value)
                        found_match = True
                        break
                
                if not found_match:
                    # Неизвестный символ
                    tokens.append(Token(TokenType.UNKNOWN, line[pos], line_num, pos + 1))
                    pos += 1
        
        tokens.append(Token(TokenType.EOF, '', len(lines) + 1, 1))
        return tokens

# ============== AST NODES ==============

class ASTNode(ABC):
    pass

class Expression(ASTNode):
    pass

class Statement(ASTNode):
    pass

@dataclass
class NumberLiteral(Expression):
    value: Union[int, float]

@dataclass
class StringLiteral(Expression):
    value: str

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class BinaryOperation(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class PrintStatement(Statement):
    expression: Expression

@dataclass
class AssignmentStatement(Statement):
    identifier: str
    expression: Expression

@dataclass
class Program(ASTNode):
    statements: List[Statement]

# ============== PARSER ==============

class ParseError(Exception):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at line {token.line}:{token.column}")

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
    
    def current_token(self) -> Token:
        if self.position >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.position]
    
    def advance(self) -> Token:
        current = self.current_token()
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return current
    
    def match(self, expected_type: TokenType) -> bool:
        return self.current_token().type == expected_type
    
    def consume(self, expected_type: TokenType, error_message: str = "") -> Token:
        if self.match(expected_type):
            return self.advance()
        
        if not error_message:
            error_message = f"Expected {expected_type.name}, got {self.current_token().type.name}"
        
        raise ParseError(error_message, self.current_token())
    
    def skip_newlines(self) -> None:
        while self.match(TokenType.NEWLINE):
            self.advance()
    
    def parse(self) -> Program:
        statements = []
        self.skip_newlines()
        
        while not self.match(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue
            
            try:
                stmt = self.parse_statement()
                statements.append(stmt)
            except ParseError as e:
                print(f"❌ Parse error: {e}")
                # Skip to next line for error recovery
                while not self.match(TokenType.NEWLINE) and not self.match(TokenType.EOF):
                    self.advance()
        
        return Program(statements)
    
    def parse_statement(self) -> Statement:
        if self.match(TokenType.PRINT):
            return self.parse_print_statement()
        elif self.match(TokenType.LET):
            return self.parse_assignment_statement()
        else:
            raise ParseError(f"Unexpected token: {self.current_token().value}", self.current_token())
    
    def parse_print_statement(self) -> PrintStatement:
        self.consume(TokenType.PRINT)
        expression = self.parse_expression()
        return PrintStatement(expression)
    
    def parse_assignment_statement(self) -> AssignmentStatement:
        self.consume(TokenType.LET)
        identifier_token = self.consume(TokenType.IDENTIFIER, "Expected variable name after 'let'")
        self.consume(TokenType.ASSIGN, "Expected '=' after variable name")
        expression = self.parse_expression()
        return AssignmentStatement(identifier_token.value, expression)
    
    def parse_expression(self) -> Expression:
        return self.parse_addition()
    
    def parse_addition(self) -> Expression:
        left = self.parse_multiplication()
        
        while self.match(TokenType.PLUS) or self.match(TokenType.MINUS):
            operator = self.advance().value
            right = self.parse_multiplication()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_multiplication(self) -> Expression:
        left = self.parse_primary()
        
        while self.match(TokenType.MULTIPLY) or self.match(TokenType.DIVIDE):
            operator = self.advance().value
            right = self.parse_primary()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_primary(self) -> Expression:
        if self.match(TokenType.NUMBER):
            token = self.advance()
            if '.' in token.value:
                return NumberLiteral(float(token.value))
            else:
                return NumberLiteral(int(token.value))
        
        elif self.match(TokenType.STRING):
            token = self.advance()
            return StringLiteral(token.value[1:-1])  # Remove quotes
        
        elif self.match(TokenType.IDENTIFIER):
            token = self.advance()
            return Identifier(token.value)
        
        else:
            raise ParseError(f"Unexpected token in expression: {self.current_token().value}", 
                           self.current_token())

# ============== INTERPRETER ==============

class RuntimeError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class Interpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.output: List[str] = []  # Для сохранения вывода
    
    def interpret(self, program: Program) -> List[str]:
        """Выполняет программу и возвращает весь вывод"""
        self.output = []
        self.variables = {}
        
        for statement in program.statements:
            try:
                self.execute_statement(statement)
            except RuntimeError as e:
                error_msg = f"❌ Runtime error: {e.message}"
                print(error_msg)
                self.output.append(error_msg)
        
        return self.output
    
    def execute_statement(self, statement: Statement) -> None:
        """Выполняет одно утверждение"""
        if isinstance(statement, PrintStatement):
            value = self.evaluate_expression(statement.expression)
            output_line = str(value)
            print(output_line)
            self.output.append(output_line)
        
        elif isinstance(statement, AssignmentStatement):
            value = self.evaluate_expression(statement.expression)
            self.variables[statement.identifier] = value
            # Для отладки можно раскомментировать:
            # print(f"[DEBUG] {statement.identifier} = {value}")
        
        else:
            raise RuntimeError(f"Unknown statement type: {type(statement)}")
    
    def evaluate_expression(self, expression: Expression) -> Any:
        """Вычисляет выражение и возвращает значение"""
        if isinstance(expression, NumberLiteral):
            return expression.value
        
        elif isinstance(expression, StringLiteral):
            return expression.value
        
        elif isinstance(expression, Identifier):
            if expression.name not in self.variables:
                raise RuntimeError(f"Undefined variable: '{expression.name}'")
            return self.variables[expression.name]
        
        elif isinstance(expression, BinaryOperation):
            left_val = self.evaluate_expression(expression.left)
            right_val = self.evaluate_expression(expression.right)
            return self.apply_binary_operation(left_val, expression.operator, right_val)
        
        else:
            raise RuntimeError(f"Unknown expression type: {type(expression)}")
    
    def apply_binary_operation(self, left: Any, operator: str, right: Any) -> Any:
        """Применяет бинарную операцию"""
        
        # Сложение
        if operator == '+':
            # Числа
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            # Строки
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            # Строка + число или число + строка
            elif isinstance(left, str) and isinstance(right, (int, float)):
                return left + str(right)
            elif isinstance(left, (int, float)) and isinstance(right, str):
                return str(left) + right
            else:
                raise RuntimeError(f"Cannot add {type(left).__name__} and {type(right).__name__}")
        
        # Остальные операции только для чисел
        elif operator in ['-', '*', '/']:
            if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
                raise RuntimeError(f"Cannot apply '{operator}' to {type(left).__name__} and {type(right).__name__}")
            
            if operator == '-':
                return left - right
            elif operator == '*':
                return left * right
            elif operator == '/':
                if right == 0:
                    raise RuntimeError("Division by zero")
                return left / right
        
        else:
            raise RuntimeError(f"Unknown operator: '{operator}'")

# ============== MAIN DOROLANG CLASS ==============

class DoroLang:
    """Главный класс языка DoroLang"""
    
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.interpreter = Interpreter()
    
    def run(self, source_code: str, show_details: bool = False) -> List[str]:
        """Выполняет код на DoroLang"""
        try:
            # Lexical analysis
            if show_details:
                print("🔍 Lexical Analysis...")
            self.lexer = Lexer(source_code)
            tokens = self.lexer.tokenize()
            
            if show_details:
                print(f"   Found {len(tokens)} tokens")
            
            # Parsing
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
            
            return output
            
        except Exception as e:
            error_msg = f"❌ Error: {e}"
            print(error_msg)
            return [error_msg]
    
    def run_interactive(self):
        """Интерактивный режим (REPL)"""
        print("=" * 50)
        print("🎉 Welcome to DoroLang Interactive Mode!")
        print("Type your code and press Enter to execute.")
        print("Type 'exit' or 'quit' to leave.")
        print("Type 'vars' to see all variables.")
        print("Type 'clear' to clear variables.")
        print("=" * 50)
        
        while True:
            try:
                line = input("DoroLang> ").strip()
                
                if line.lower() in ['exit', 'quit']:
                    print("👋 Goodbye!")
                    break
                elif line.lower() == 'vars':
                    if self.interpreter.variables:
                        print("📊 Variables:")
                        for name, value in self.interpreter.variables.items():
                            print(f"   {name} = {value} ({type(value).__name__})")
                    else:
                        print("📊 No variables defined")
                    continue
                elif line.lower() == 'clear':
                    self.interpreter.variables.clear()
                    print("🧹 Variables cleared")
                    continue
                elif not line:
                    continue
                
                # Execute the line
                self.run(line, show_details=False)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break

# ============== EXAMPLES & TESTING ==============

def run_examples():
    """Запускает примеры кода на DoroLang"""
    
    examples = [
        ("Basic Hello World", '''
say "Hello, DoroLang!"
say "Created by Dorofii"
        '''),
        
        ("Variables and Math", '''
kas name = "Dorofii"
kas age = 20
say "Name: " + name
say "Age: " + age
say "Next year: " + (age + 1)
        '''),
        
        ("Complex Expressions", '''
kas a = 10
kas b = 5
say "a + b = " + (a + b)
say "a - b = " + (a - b)
say "a * b = " + (a * b)
say "a / b = " + (a / b)
say "Complex: " + (a * 2 + b / 2)
        '''),
        
        ("String Operations", '''
kas first = "Doro"
kas last = "Lang"
kas full = first + last
say "Full name: " + full
say "Length info: " + full + " programming language"
        ''')
    ]
    
    dorolang = DoroLang()
    
    for title, code in examples:
        print("\n" + "=" * 60)
        print(f"📝 Example: {title}")
        print("=" * 60)
        print("Source code:")
        print(code.strip())
        print("\n🚀 Output:")
        print("-" * 30)
        
        dorolang.interpreter.variables.clear()  # Reset variables for each example
        dorolang.run(code.strip(), show_details=False)
        
        print("-" * 30)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            # Интерактивный режим
            dorolang = DoroLang()
            dorolang.run_interactive()
        elif sys.argv[1] == "examples":
            # Запуск примеров
            run_examples()
        else:
            # Запуск файла
            try:
                with open(sys.argv[1], 'r', encoding='utf-8') as f:
                    code = f.read()
                dorolang = DoroLang()
                dorolang.run(code, show_details=True)
            except FileNotFoundError:
                print(f"❌ File not found: {sys.argv[1]}")
    else:
        # Демонстрация по умолчанию
        print("🎉 DoroLang - Programming Language Demo")
        run_examples()
        
        print("\n" + "=" * 60)
        print("🎯 Usage:")
        print("  python dorolang.py                 # Run examples")
        print("  python dorolang.py interactive     # Interactive mode")  
        print("  python dorolang.py examples        # Run all examples")
        print("  python dorolang.py program.doro    # Run file")
        print("=" * 60)
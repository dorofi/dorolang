from abc import ABC, abstractmethod
from typing import List, Optional, Union
from dataclasses import dataclass

# Импортируем наш лексер
from enum import Enum, auto
import re

# Копируем определения из лексера (в реальном проекте это было бы в отдельных файлах)
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

# ============== AST NODE DEFINITIONS ==============

class ASTNode(ABC):
    """Базовый класс для всех узлов AST"""
    pass

class Expression(ASTNode):
    """Базовый класс для всех выражений"""
    pass

class Statement(ASTNode):
    """Базовый класс для всех утверждений"""
    pass

# EXPRESSIONS (выражения - то что возвращает значение)

@dataclass
class NumberLiteral(Expression):
    """Числовой литерал: 42, 3.14"""
    value: Union[int, float]
    
    def __str__(self):
        return f"Number({self.value})"

@dataclass
class StringLiteral(Expression):
    """Строковый литерал: "hello", 'world'"""
    value: str
    
    def __str__(self):
        return f"String({self.value})"

@dataclass
class Identifier(Expression):
    """Идентификатор переменной: name, age"""
    name: str
    
    def __str__(self):
        return f"Var({self.name})"

@dataclass
class BinaryOperation(Expression):
    """Бинарные операции: a + b, x * y"""
    left: Expression
    operator: str
    right: Expression
    
    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

# STATEMENTS (утверждения - то что выполняет действия)

@dataclass
class PrintStatement(Statement):
    """Print утверждение: print expression"""
    expression: Expression
    
    def __str__(self):
        return f"Print({self.expression})"

@dataclass
class AssignmentStatement(Statement):
    """Присваивание: let name = expression"""
    identifier: str
    expression: Expression
    
    def __str__(self):
        return f"Assign({self.identifier} = {self.expression})"

@dataclass
class Program(ASTNode):
    """Корень программы - список утверждений"""
    statements: List[Statement]
    
    def __str__(self):
        statements_str = "\n  ".join(str(stmt) for stmt in self.statements)
        return f"Program:\n  {statements_str}"

# ============== PARSER ==============

class ParseError(Exception):
    """Исключение для ошибок парсинга"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at line {token.line}, column {token.column}")

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
    
    def current_token(self) -> Token:
        """Возвращает текущий токен"""
        if self.position >= len(self.tokens):
            return self.tokens[-1]  # EOF токен
        return self.tokens[self.position]
    
    def peek_token(self, offset: int = 1) -> Token:
        """Смотрит на токен впереди"""
        peek_pos = self.position + offset
        if peek_pos >= len(self.tokens):
            return self.tokens[-1]  # EOF токен
        return self.tokens[peek_pos]
    
    def advance(self) -> Token:
        """Перемещается к следующему токену и возвращает предыдущий"""
        current = self.current_token()
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return current
    
    def match(self, expected_type: TokenType) -> bool:
        """Проверяет соответствие текущего токена ожидаемому типу"""
        return self.current_token().type == expected_type
    
    def consume(self, expected_type: TokenType, error_message: str = "") -> Token:
        """Потребляет токен ожидаемого типа или выбрасывает ошибку"""
        if self.match(expected_type):
            return self.advance()
        
        if not error_message:
            error_message = f"Expected {expected_type.name}, got {self.current_token().type.name}"
        
        raise ParseError(error_message, self.current_token())
    
    def skip_newlines(self) -> None:
        """Пропускает все токены новых строк"""
        while self.match(TokenType.NEWLINE):
            self.advance()
    
    def parse(self) -> Program:
        """Главный метод парсинга - парсит всю программу"""
        statements = []
        
        self.skip_newlines()  # Пропускаем пустые строки в начале
        
        while not self.match(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue
            
            try:
                stmt = self.parse_statement()
                statements.append(stmt)
            except ParseError as e:
                print(f"Parse error: {e}")
                # Пропускаем до следующей строки для восстановления
                while not self.match(TokenType.NEWLINE) and not self.match(TokenType.EOF):
                    self.advance()
        
        return Program(statements)
    
    def parse_statement(self) -> Statement:
        """Парсит одно утверждение"""
        # Print statement
        if self.match(TokenType.PRINT):
            return self.parse_print_statement()
        
        # Assignment statement (let x = ...)
        elif self.match(TokenType.LET):
            return self.parse_assignment_statement()
        
        else:
            raise ParseError(f"Unexpected token: {self.current_token().value}", self.current_token())
    
    def parse_print_statement(self) -> PrintStatement:
        """Парсит print утверждение"""
        self.consume(TokenType.PRINT)  # Потребляем 'print'
        expression = self.parse_expression()  # Парсим выражение для печати
        return PrintStatement(expression)
    
    def parse_assignment_statement(self) -> AssignmentStatement:
        """Парсит присваивание: let name = expression"""
        self.consume(TokenType.LET)  # Потребляем 'let'
        
        # Получаем имя переменной
        identifier_token = self.consume(TokenType.IDENTIFIER, "Expected variable name after 'let'")
        identifier_name = identifier_token.value
        
        # Потребляем знак присваивания
        self.consume(TokenType.ASSIGN, "Expected '=' after variable name")
        
        # Парсим выражение справа от =
        expression = self.parse_expression()
        
        return AssignmentStatement(identifier_name, expression)
    
    def parse_expression(self) -> Expression:
        """Парсит выражение (с учетом приоритета операторов)"""
        return self.parse_addition()
    
    def parse_addition(self) -> Expression:
        """Парсит сложение и вычитание (низший приоритет)"""
        left = self.parse_multiplication()
        
        while self.match(TokenType.PLUS) or self.match(TokenType.MINUS):
            operator = self.advance().value
            right = self.parse_multiplication()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_multiplication(self) -> Expression:
        """Парсит умножение и деление (высший приоритет)"""
        left = self.parse_primary()
        
        while self.match(TokenType.MULTIPLY) or self.match(TokenType.DIVIDE):
            operator = self.advance().value
            right = self.parse_primary()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_primary(self) -> Expression:
        """Парсит первичные выражения (числа, строки, переменные)"""
        # Числа
        if self.match(TokenType.NUMBER):
            token = self.advance()
            # Определяем int или float
            if '.' in token.value:
                return NumberLiteral(float(token.value))
            else:
                return NumberLiteral(int(token.value))
        
        # Строки
        elif self.match(TokenType.STRING):
            token = self.advance()
            # Убираем кавычки
            string_value = token.value[1:-1]  # Убираем первый и последний символ (кавычки)
            return StringLiteral(string_value)
        
        # Идентификаторы (переменные)
        elif self.match(TokenType.IDENTIFIER):
            token = self.advance()
            return Identifier(token.value)
        
        else:
            raise ParseError(f"Unexpected token in expression: {self.current_token().value}", 
                           self.current_token())
    
    def pretty_print_ast(self, node: ASTNode, indent: int = 0) -> None:
        """Красиво выводит AST дерево"""
        prefix = "  " * indent
        
        if isinstance(node, Program):
            print(f"{prefix}Program:")
            for stmt in node.statements:
                self.pretty_print_ast(stmt, indent + 1)
        
        elif isinstance(node, PrintStatement):
            print(f"{prefix}PrintStatement:")
            self.pretty_print_ast(node.expression, indent + 1)
        
        elif isinstance(node, AssignmentStatement):
            print(f"{prefix}Assignment: {node.identifier} =")
            self.pretty_print_ast(node.expression, indent + 1)
        
        elif isinstance(node, BinaryOperation):
            print(f"{prefix}BinaryOp: {node.operator}")
            self.pretty_print_ast(node.left, indent + 1)
            self.pretty_print_ast(node.right, indent + 1)
        
        elif isinstance(node, NumberLiteral):
            print(f"{prefix}Number: {node.value}")
        
        elif isinstance(node, StringLiteral):
            print(f"{prefix}String: \"{node.value}\"")
        
        elif isinstance(node, Identifier):
            print(f"{prefix}Variable: {node.name}")


# ============== ПРОСТОЙ ЛЕКСЕР ДЛЯ ТЕСТИРОВАНИЯ ==============

class SimpleLexer:
    """Упрощенная версия лексера для тестирования парсера"""
    
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        
        self.token_patterns = [
            (r'print', TokenType.PRINT),
            (r'let', TokenType.LET),
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
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            pos = 0
            while pos < len(line):
                if line[pos] == ' ':
                    pos += 1
                    continue
                
                found_match = False
                for pattern, token_type in self.token_patterns:
                    match = re.match(pattern, line[pos:])
                    if match:
                        value = match.group(0)
                        tokens.append(Token(token_type, value, line_num, pos + 1))
                        pos += len(value)
                        found_match = True
                        break
                
                if not found_match:
                    pos += 1
        
        tokens.append(Token(TokenType.EOF, '', len(lines), 1))
        return tokens


# ============== ТЕСТИРОВАНИЕ ==============

if __name__ == "__main__":
    # Тестовый код на DoroLang
    test_code = '''
print "Hello, DoroLang!"
print 42
let name = "Dorofii"
print name
let age = 25
print age + 5
print "Age is " + age
let result = 10 * 2 + 3
print result
'''
    
    print("=== ИСХОДНЫЙ КОД ===")
    print(test_code)
    print("\n" + "="*50)
    
    # Токенизация
    lexer = SimpleLexer(test_code)
    tokens = lexer.tokenize()
    
    print("\n=== ТОКЕНЫ ===")
    for i, token in enumerate(tokens):
        print(f"{i:2}: {token.type.name:12} '{token.value}'")
    
    print("\n" + "="*50)
    
    # Парсинг
    parser = Parser(tokens)
    try:
        ast = parser.parse()
        
        print("\n=== ABSTRACT SYNTAX TREE ===")
        parser.pretty_print_ast(ast)
        
        print(f"\n=== СВОДКА ===")
        print(f"✅ Токенов: {len(tokens)}")
        print(f"✅ Утверждений: {len(ast.statements)}")
        print("✅ Парсер готов! 🎉")
        
    except ParseError as e:
        print(f"\n❌ Ошибка парсинга: {e}")
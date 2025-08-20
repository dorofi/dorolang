"""
DoroLang Parser - Синтаксический анализатор
Строит абстрактное синтаксическое дерево (AST) из токенов

Автор: Dorofii Karnaukh
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

# Импортируем токены из лексера
from lexer import Token, TokenType


# ============== AST NODE DEFINITIONS ==============

class ASTNode(ABC):
    """Базовый класс для всех узлов AST"""
    pass


class Expression(ASTNode):
    """Базовый класс для всех выражений (возвращают значение)"""
    pass


class Statement(ASTNode):
    """Базовый класс для всех утверждений (выполняют действия)"""
    pass


# ============== EXPRESSIONS ==============

@dataclass
class NumberLiteral(Expression):
    """Числовой литерал: 42, 3.14"""
    value: float
    
    def __str__(self):
        return f"Number({self.value})"


@dataclass
class BooleanLiteral(Expression):
    """Булев литерал: true, false"""
    value: bool
    
    def __str__(self):
        return f"Boolean({self.value})"


@dataclass
class StringLiteral(Expression):
    """Строковый литерал: "hello", 'world'"""
    value: str
    
    def __str__(self):
        return f'String("{self.value}")'


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


@dataclass
class UnaryOperation(Expression):
    """Унарные операции: -x, +y"""
    operator: str
    operand: Expression
    
    def __str__(self):
        return f"({self.operator}{self.operand})"


@dataclass
class ParenthesizedExpression(Expression):
    """Выражения в скобках: (expression)"""
    expression: Expression
    
    def __str__(self):
        return f"({self.expression})"


# ============== STATEMENTS ==============

@dataclass
class SayStatement(Statement):
    """Say утверждение: say expression"""
    expression: Expression
    
    def __str__(self):
        return f"Say({self.expression})"


@dataclass
class AssignmentStatement(Statement):
    """Присваивание: kas name = expression"""
    identifier: str
    expression: Expression
    
    def __str__(self):
        return f"Assign({self.identifier} = {self.expression})"


@dataclass
class BlockStatement(Statement):
    """Блок кода: { statement* }"""
    statements: List[Statement]
    
    def __str__(self):
        return f"Block(...)"


@dataclass
class IfStatement(Statement):
    """If-Else утверждение"""
    condition: Expression
    then_branch: BlockStatement
    else_branch: Optional[Statement] # Может быть IfStatement или BlockStatement


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
        super().__init__(f"Parse Error: {message} at line {token.line}:{token.column}")


class Parser:
    """
    Синтаксический анализатор для DoroLang
    
    Использует рекурсивный спуск для построения AST
    Грамматика (приоритет операторов):
    
    program         → statement*
    statement       → sayStatement | assignStatement | ifStatement | blockStatement
    blockStatement  → "{" statement* "}"
    ifStatement     → "if" "(" expression ")" statement ("else" statement)?
    sayStatement    → "say" expression
    assignStatement  → "kas" IDENTIFIER "=" expression
    expression      → comparison
    comparison      → addition (("==" | "!=" | "<" | ">" | "<=" | ">=") addition)*
    addition        → multiplication (("+" | "-") multiplication)*
    multiplication  → unary (("*" | "/" | "%") unary)*
    unary           → ("-" | "+") unary | primary
    primary         → NUMBER | STRING | BOOLEAN | IDENTIFIER | "(" expression ")"
    """
    
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
    
    def match(self, *expected_types: TokenType) -> bool:
        """Проверяет соответствие текущего токена любому из ожидаемых типов"""
        return self.current_token().type in expected_types
    
    def consume(self, expected_type: TokenType, error_message: str = "") -> Token:
        """Потребляет токен ожидаемого типа или выбрасывает ошибку"""
        if self.match(expected_type):
            return self.advance()
        
        if not error_message:
            error_message = (f"Expected {expected_type.name}, "
                           f"got {self.current_token().type.name} '{self.current_token().value}'")
        
        raise ParseError(error_message, self.current_token())
    
    def skip_newlines(self) -> None:
        """Пропускает все токены новых строк"""
        while self.match(TokenType.NEWLINE):
            self.advance()
    
    def parse(self) -> Program:
        """
        Главный метод парсинга - парсит всю программу
        
        Returns:
            Program: Корневой узел AST
            
        Raises:
            ParseError: При синтаксических ошибках
        """
        statements = []
        
        self.skip_newlines()  # Пропускаем пустые строки в начале
        
        while not self.match(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue
            
            stmt = self.parse_statement()
            if stmt:  # Проверяем что утверждение не None
                statements.append(stmt)
        
        return Program(statements)
    
    def parse_statement(self) -> Optional[Statement]:
        """Парсит одно утверждение"""
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.match(TokenType.SAY):
            return self.parse_say_statement()
        elif self.match(TokenType.KAS):
            return self.parse_assignment_statement()
        elif self.match(TokenType.LBRACE):
            return self.parse_block_statement()
        else:
            raise ParseError(
                f"Unexpected token: '{self.current_token().value}'", 
                self.current_token()
            )
    
    def parse_if_statement(self) -> IfStatement:
        """Парсит if-else утверждение"""
        self.consume(TokenType.IF)
        self.consume(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after if condition")
        
        then_branch = self.parse_statement()
        if not isinstance(then_branch, BlockStatement):
             raise ParseError("Expected a block statement '{...}' after if condition", self.current_token())

        else_branch = None
        if self.match(TokenType.ELSE):
            self.advance() # consume 'else'
            else_branch = self.parse_statement()
            if not isinstance(else_branch, (BlockStatement, IfStatement)):
                raise ParseError("Expected a block statement '{...}' or another 'if' after 'else'", self.current_token())

        return IfStatement(condition, then_branch, else_branch)

    def parse_block_statement(self) -> BlockStatement:
        """Парсит блок кода: { ... }"""
        self.consume(TokenType.LBRACE)
        self.skip_newlines()  # Разрешаем новые строки после '{'
        
        statements = []
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            statements.append(self.parse_statement())
            self.skip_newlines()  # Разрешаем новые строки после каждого утверждения
            
        self.consume(TokenType.RBRACE, "Expected '}' to close block")
        return BlockStatement(statements)

    def parse_say_statement(self) -> SayStatement:
        """Парсит say утверждение"""
        self.consume(TokenType.SAY)  # Потребляем 'say'
        expression = self.parse_expression()  # Парсим выражение для вывода
        return SayStatement(expression)
    
    def parse_assignment_statement(self) -> AssignmentStatement:
        """Парсит присваивание: kas name = expression"""
        self.consume(TokenType.KAS)  # Потребляем 'kas'
        
        # Получаем имя переменной
        identifier_token = self.consume(
            TokenType.IDENTIFIER, 
            "Expected variable name after 'kas'"
        )
        identifier_name = identifier_token.value
        
        # Потребляем знак присваивания
        self.consume(TokenType.ASSIGN, "Expected '=' after variable name")
        
        # Парсим выражение справа от =
        expression = self.parse_expression()
        
        return AssignmentStatement(identifier_name, expression)
    
    def parse_expression(self) -> Expression:
        """Парсит выражение (точка входа в иерархию приоритетов)"""
        return self.parse_comparison()

    def parse_comparison(self) -> Expression:
        """Парсит операторы сравнения"""
        left = self.parse_addition()
        
        while self.match(TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            operator = self.advance().value
            right = self.parse_addition()
            left = BinaryOperation(left, operator, right)
            
        return left
    
    def parse_addition(self) -> Expression:
        """Парсит сложение и вычитание (низший приоритет)"""
        left = self.parse_multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.advance().value
            right = self.parse_multiplication()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_multiplication(self) -> Expression:
        """Парсит умножение, деление и модulo (средний приоритет)"""
        left = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.advance().value
            right = self.parse_unary()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_unary(self) -> Expression:
        """Парсит унарные операции (высший приоритет)"""
        if self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.advance().value
            operand = self.parse_unary()  # Рекурсивный вызов для поддержки --x
            return UnaryOperation(operator, operand)
        
        return self.parse_primary()
    
    def parse_primary(self) -> Expression:
        """Парсит первичные выражения"""
        # Скобки
        if self.match(TokenType.LPAREN):
            self.advance()  # consume '('
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return ParenthesizedExpression(expr)
        
        # Числа
        elif self.match(TokenType.NUMBER):
            token = self.advance()
            return NumberLiteral(float(token.value))
        
        # Строки
        elif self.match(TokenType.STRING):
            token = self.advance()
            # Обрабатываем строковый литерал (убираем кавычки и escape)
            string_value = self._process_string_literal(token.value)
            return StringLiteral(string_value)

        # Булевы значения
        elif self.match(TokenType.TRUE):
            self.advance()
            return BooleanLiteral(True)
        
        elif self.match(TokenType.FALSE):
            self.advance()
            return BooleanLiteral(False)
        
        # Идентификаторы (переменные)
        elif self.match(TokenType.IDENTIFIER):
            token = self.advance()
            return Identifier(token.value)
        
        else:
            raise ParseError(
                f"Unexpected token in expression: '{self.current_token().value}'", 
                self.current_token()
            )
    
    def _process_string_literal(self, raw_string: str) -> str:
        """Обрабатывает строковый литерал (убирает кавычки и обрабатывает escape)"""
        # Убираем внешние кавычки
        content = raw_string[1:-1]
        
        # Простая обработка escape-последовательностей
        content = content.replace('\\n', '\n')
        content = content.replace('\\t', '\t')
        content = content.replace('\\r', '\r')
        content = content.replace('\\\\', '\\')
        content = content.replace('\\"', '"')
        content = content.replace("\\'", "'")
        
        return content
    
    def pretty_print_ast(self, node: ASTNode, indent: int = 0) -> None:
        """Красиво выводит AST дерево"""
        prefix = "  " * indent
        
        if isinstance(node, Program):
            print(f"{prefix}Program:")
            for stmt in node.statements:
                self.pretty_print_ast(stmt, indent + 1)
        
        elif isinstance(node, SayStatement):
            print(f"{prefix}SayStatement:")
            self.pretty_print_ast(node.expression, indent + 1)
        
        elif isinstance(node, AssignmentStatement):
            print(f"{prefix}Assignment: {node.identifier} =")
            self.pretty_print_ast(node.expression, indent + 1)
        
        elif isinstance(node, BinaryOperation):
            print(f"{prefix}BinaryOp: '{node.operator}'")
            print(f"{prefix}  Left:")
            self.pretty_print_ast(node.left, indent + 2)
            print(f"{prefix}  Right:")
            self.pretty_print_ast(node.right, indent + 2)
        
        elif isinstance(node, UnaryOperation):
            print(f"{prefix}UnaryOp: '{node.operator}'")
            self.pretty_print_ast(node.operand, indent + 1)
        
        elif isinstance(node, ParenthesizedExpression):
            print(f"{prefix}Parentheses:")
            self.pretty_print_ast(node.expression, indent + 1)
        
        elif isinstance(node, NumberLiteral):
            print(f"{prefix}Number: {node.value}")
        
        elif isinstance(node, StringLiteral):
            print(f"{prefix}String: \"{node.value}\"")
        
        elif isinstance(node, Identifier):
            print(f"{prefix}Variable: {node.name}")


# Тестирование модуля
if __name__ == "__main__":
    from lexer import Lexer
    
    # Тестовый код
    test_code = '''
say "Parser test!"
kas x = -(5 + 3) * 2
kas y = (10 + 5) % 4
kas z = -(-x + y)
say "Result: " + z
'''
    
    print("=== TESTING PARSER ===")
    print("Source code:")
    print(test_code)
    print("\n" + "="*40)
    
    try:
        # Токенизация
        lexer = Lexer(test_code)
        tokens = lexer.tokenize()
        print(f"✅ Lexer: {len(tokens)} tokens")
        
        # Парсинг
        parser = Parser(tokens)
        ast = parser.parse()
        print(f"✅ Parser: {len(ast.statements)} statements")
        
        print("\n=== AST ===")
        parser.pretty_print_ast(ast)
        
        print("\n✅ Parser test passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
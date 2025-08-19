"""
DoroLang Lexer - Лексический анализатор
Отвечает за разбор исходного кода на токены

Автор: Dorofii Karnaukh
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Типы токенов в DoroLang"""
    # Литералы
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    
    # Ключевые слова
    SAY = auto()        # say
    KAS = auto()        # kas
    
    # Операторы
    ASSIGN = auto()     # =
    PLUS = auto()       # +
    MINUS = auto()      # -
    MULTIPLY = auto()   # *
    DIVIDE = auto()     # /
    MODULO = auto()     # %
    
    # Разделители
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    
    # Специальные
    NEWLINE = auto()
    EOF = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """Представление одного токена"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"{self.type.name}({self.value}) at {self.line}:{self.column}"


class LexerError(Exception):
    """Исключение лексера"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer Error: {message} at line {line}:{column}")


class Lexer:
    """
    Лексический анализатор для DoroLang
    
    Преобразует исходный код в последовательность токенов
    """
    
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
        # Паттерны для токенов (порядок важен!)
        self.token_patterns = [
            # Ключевые слова (должны быть перед идентификаторами)
            (r'say\b', TokenType.SAY),
            (r'kas\b', TokenType.KAS),
            
            # Литералы
            (r'\d+\.?\d*', TokenType.NUMBER),
            (r'"(?:[^"\\]|\\.)*"', TokenType.STRING),
            (r"'(?:[^'\\]|\\.)*'", TokenType.STRING),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
            
            # Операторы
            (r'=', TokenType.ASSIGN),
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'%', TokenType.MODULO),
            
            # Разделители
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            
            # Специальные
            (r'\n', TokenType.NEWLINE),
        ]
    
    def current_char(self) -> Optional[str]:
        """Возвращает текущий символ или None если достигли конца"""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Смотрит на символ впереди без перемещения позиции"""
        peek_pos = self.position + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self) -> None:
        """Перемещаемся к следующему символу"""
        if self.position < len(self.source):
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def skip_whitespace(self) -> None:
        """Пропускаем пробелы и табы (но не новые строки)"""
        while (self.current_char() is not None and 
               self.current_char() in ' \t\r'):
            self.advance()
    
    def skip_comment(self) -> None:
        """Пропускаем комментарии начинающиеся с #"""
        if self.current_char() == '#':
            # Пропускаем до конца строки
            while (self.current_char() is not None and 
                   self.current_char() != '\n'):
                self.advance()
    
    def read_string(self, quote_char: str) -> str:
        """Читаем строку с правильной обработкой escape-последовательностей"""
        result = quote_char  # Включаем открывающую кавычку
        self.advance()  # Пропускаем открывающую кавычку
        
        while (self.current_char() is not None and 
               self.current_char() != quote_char):
            if self.current_char() == '\\':
                # Обработка escape-последовательностей
                result += self.current_char()
                self.advance()
                if self.current_char() is not None:
                    result += self.current_char()
                    self.advance()
            else:
                result += self.current_char()
                self.advance()
        
        if self.current_char() == quote_char:
            result += self.current_char()  # Включаем закрывающую кавычку
            self.advance()
        else:
            raise LexerError(
                f"Unterminated string starting with {quote_char}",
                self.line, self.column
            )
        
        return result
    
    def tokenize(self) -> List[Token]:
        """
        Основной метод токенизации
        
        Returns:
            List[Token]: Список токенов
            
        Raises:
            LexerError: При ошибках лексического анализа
        """
        self.tokens = []
        
        while self.position < len(self.source):
            self.skip_whitespace()
            
            # Конец файла
            if self.current_char() is None:
                break
            
            # Комментарии
            if self.current_char() == '#':
                self.skip_comment()
                continue
            
            # Сохраняем текущую позицию для токена
            token_line = self.line
            token_column = self.column
            
            # Строки в кавычках
            if self.current_char() in '"\'':
                quote_char = self.current_char()
                try:
                    string_value = self.read_string(quote_char)
                    self.tokens.append(Token(TokenType.STRING, string_value, token_line, token_column))
                    continue
                except LexerError:
                    raise  # Перебрасываем ошибку дальше
            
            # Пробуем найти совпадение с регулярными выражениями
            found_match = False
            remaining_source = self.source[self.position:]
            
            for pattern, token_type in self.token_patterns:
                match = re.match(pattern, remaining_source)
                if match:
                    token_value = match.group(0)
                    self.tokens.append(Token(token_type, token_value, token_line, token_column))
                    
                    # Перемещаем позицию
                    for _ in range(len(token_value)):
                        self.advance()
                    
                    found_match = True
                    break
            
            if not found_match:
                # Неизвестный символ
                unknown_char = self.current_char()
                raise LexerError(
                    f"Unknown character '{unknown_char}'",
                    self.line, self.column
                )
        
        # Добавляем EOF токен
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
    
    def print_tokens(self) -> None:
        """Красиво выводим все токены для отладки"""
        print("=== TOKENS ===")
        for i, token in enumerate(self.tokens):
            print(f"{i:2}: {token}")


# Тестирование модуля
if __name__ == "__main__":
    # Тестовый код
    test_code = '''
# Комментарий
say "Hello, DoroLang!"
kas x = 42
kas y = (x + 10) % 3
say "Result: " + y
'''
    
    print("=== TESTING LEXER ===")
    print("Source code:")
    print(test_code)
    print("\n" + "="*40)
    
    try:
        lexer = Lexer(test_code)
        tokens = lexer.tokenize()
        lexer.print_tokens()
        
        print(f"\n✅ Lexer test passed! Found {len(tokens)} tokens.")
        
        # Проверяем что нашли все ожидаемые токены
        token_types = [token.type for token in tokens]
        expected = [TokenType.SAY, TokenType.KAS, TokenType.LPAREN, TokenType.MODULO]
        
        for expected_type in expected:
            if expected_type in token_types:
                print(f"✅ Found {expected_type.name}")
            else:
                print(f"❌ Missing {expected_type.name}")
                
    except LexerError as e:
        print(f"❌ Lexer error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
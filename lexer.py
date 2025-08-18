import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    
    # Keywords
    PRINT = auto()
    LET = auto()    # для переменных: let x = 5
    
    # Operators
    ASSIGN = auto()     # =
    PLUS = auto()       # +
    MINUS = auto()      # -
    MULTIPLY = auto()   # *
    DIVIDE = auto()     # /
    
    # Delimiters
    NEWLINE = auto()
    EOF = auto()        # End of file
    
    # Special
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
        
        # Регулярные выражения для токенов
        self.token_patterns = [
            (r'print', TokenType.PRINT),
            (r'let', TokenType.LET),
            (r'\d+\.?\d*', TokenType.NUMBER),          # 123, 12.34
            (r'"[^"]*"', TokenType.STRING),            # "hello world"
            (r"'[^']*'", TokenType.STRING),            # 'hello world'
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),  # имена переменных
            (r'=', TokenType.ASSIGN),
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
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
        """Читаем строку в кавычках"""
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
        
        return result
    
    def tokenize(self) -> List[Token]:
        """Основной метод токенизации"""
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
                string_value = self.read_string(quote_char)
                self.tokens.append(Token(TokenType.STRING, string_value, token_line, token_column))
                continue
            
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
                self.tokens.append(Token(TokenType.UNKNOWN, unknown_char, token_line, token_column))
                self.advance()
        
        # Добавляем EOF токен
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
    
    def print_tokens(self) -> None:
        """Красиво выводим все токены"""
        print("=== ТОКЕНЫ ===")
        for i, token in enumerate(self.tokens):
            print(f"{i:2}: {token.type.name:12} '{token.value}' at {token.line}:{token.column}")


# Тестируем наш лексер!
if __name__ == "__main__":
    # Пример кода на DoroLang
    sample_code = '''
# Это комментарий
print "Hello, DoroLang!"
print 42
let name = "Dorofii"
print "My name is " + name
let age = 25
print age * 2
'''
    
    print("=== ИСХОДНЫЙ КОД ===")
    print(sample_code)
    print("\n" + "="*50 + "\n")
    
    # Создаем лексер и токенизируем
    lexer = Lexer(sample_code)
    tokens = lexer.tokenize()
    
    # Выводим результат
    lexer.print_tokens()
    
    print(f"\nВсего токенов: {len(tokens)}")
    print("Лексер готов! 🎉")
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
    IF = auto()         # if
    INPUT = auto()      # input (НОВОЕ)
    ELSE = auto()       # else
    TRUE = auto()       # true
    FALSE = auto()      # false
    
    # Логические операторы (НОВЫЕ)
    AND = auto()        # and
    OR = auto()         # or
    NOT = auto()        # not
    
    # Операторы
    ASSIGN = auto()     # =
    PLUS = auto()       # +
    MINUS = auto()      # -
    MULTIPLY = auto()   # *
    DIVIDE = auto()     # /
    MODULO = auto()     # %
    
    # Операторы сравнения
    EQ = auto()         # ==
    NEQ = auto()        # !=
    LT = auto()         # <
    GT = auto()         # >
    LTE = auto()        # <=
    GTE = auto()        # >=
    
    # Разделители
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    
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
            (r'if\b', TokenType.IF),
            (r'input\b', TokenType.INPUT),  # НОВЫЙ
            (r'else\b', TokenType.ELSE),
            (r'true\b', TokenType.TRUE),
            (r'false\b', TokenType.FALSE),
            (r'and\b', TokenType.AND),      # НОВЫЙ
            (r'or\b', TokenType.OR),        # НОВЫЙ
            (r'not\b', TokenType.NOT),      # НОВЫЙ
            
            # Литералы
            (r'\d+\.?\d*', TokenType.NUMBER),
            (r'"(?:[^"\\]|\\.)*"', TokenType.STRING),
            (r"'(?:[^'\\]|\\.)*'", TokenType.STRING),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
            
            # Операторы (двухсимвольные сначала)
            (r'==', TokenType.EQ),
            (r'!=', TokenType.NEQ),
            (r'<=', TokenType.LTE),
            (r'>=', TokenType.GTE),
            (r'=', TokenType.ASSIGN), # Односимвольный = после ==
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'%', TokenType.MODULO),
            (r'<', TokenType.LT),
            (r'>', TokenType.GT),
            
            # Разделители
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            
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
    # Тестовый код с новыми возможностями
    test_code = '''
# Комментарий - тест логических операторов
say "Hello, DoroLang!"
kas x = 42
kas y = (x + 10) % 3

# Тест булевых значений и логических операторов
kas is_big = x > 30
kas is_small = y < 5
kas result = is_big and is_small

if (result) {
    say "Both conditions are true!"
} else {
    say "At least one condition is false"
}

# Тест оператора not
kas negative_result = not result
say "Negative result: " + negative_result

# Тест оператора or
if (is_big or is_small) {
    say "At least one is true"
}
'''

    # Более детальный тест для строк, чтобы убедиться, что ничего не сломалось
    string_test_code = '''
say "простая строка"
say 'и в одинарных кавычках'
say "строка с \\"экранированной кавычкой\\""
say 'и в одинарных \\'тоже\\''
say "пустая строка: """
kas my_string="строкабезпробела"
'''

    input_test_code = '''
# Тест новой функции input
kas user_name = input("Как тебя зовут? ")
say "Привет, " + user_name + "!"
'''

    def run_lexer_test(name, code):
        """Вспомогательная функция для запуска тестов и вывода результата"""
        print(f"\n===== ЗАПУСК ТЕСТА: {name} =====")
        print("Исходный код:")
        print(code)
        print("-" * 20)
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            lexer.print_tokens()
            print(f"\n✅ Тест '{name}' пройден! Найдено {len(tokens)} токенов.")
        except LexerError as e:
            print(f"❌ Ошибка лексера в тесте '{name}': {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")

    
    print("="*20 + " ТЕСТИРОВАНИЕ ЛЕКСЕРА " + "="*20)

    # Запускаем оба теста
    run_lexer_test("Логические операторы", test_code)
    run_lexer_test("Парсинг строк", string_test_code)
    run_lexer_test("Функция Input", input_test_code)

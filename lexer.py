"""
DoroLang Lexer - Lexical Analyzer
Responsible for parsing source code into tokens

Author: Dorofii Karnaukh
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Token types in DoroLang"""
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    
    # Keywords
    SAY = auto()        # say
    KAS = auto()        # kas
    IF = auto()         # if
    WHILE = auto()      # while
    FOR = auto()        # for
    FUNCTION = auto()   # function (NEW)
    RETURN = auto()     # return (NEW)
    INPUT = auto()      # input
    ELSE = auto()       # else
    TRUE = auto()       # true
    FALSE = auto()      # false
    
    # Logical operators (NEW)
    AND = auto()        # and
    OR = auto()         # or
    NOT = auto()        # not
    
    # Operators
    ASSIGN = auto()     # =
    PLUS = auto()       # +
    MINUS = auto()      # -
    MULTIPLY = auto()   # *
    DIVIDE = auto()     # /
    MODULO = auto()     # %
    
    # Comparison operators
    EQ = auto()         # ==
    NEQ = auto()        # !=
    LT = auto()         # <
    GT = auto()         # >
    LTE = auto()        # <=
    GTE = auto()        # >=
    
    # Delimiters
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    COMMA = auto()      # , (NEW)
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """Representation of a single token"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"{self.type.name}({self.value}) at {self.line}:{self.column}"


class LexerError(Exception):
    """Lexer exception"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer Error: {message} at line {line}:{column}")


class Lexer:
    """
    Lexical analyzer for DoroLang
    
    Converts source code into a sequence of tokens
    """
    
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
        # Token patterns (order matters!)
        self.token_patterns = [
            # Keywords (must be before identifiers)
            (r'say\b', TokenType.SAY),
            (r'kas\b', TokenType.KAS),
            (r'if\b', TokenType.IF),
            (r'while\b', TokenType.WHILE),
            (r'for\b', TokenType.FOR),
            (r'function\b', TokenType.FUNCTION),  # NEW
            (r'return\b', TokenType.RETURN),      # NEW
            (r'input\b', TokenType.INPUT),
            (r'else\b', TokenType.ELSE),
            (r'true\b', TokenType.TRUE),
            (r'false\b', TokenType.FALSE),
            (r'and\b', TokenType.AND),
            (r'or\b', TokenType.OR),
            (r'not\b', TokenType.NOT),
            
            # Literals
            (r'\d+\.?\d*', TokenType.NUMBER),
            (r'"(?:[^"\\]|\\.)*"', TokenType.STRING),
            (r"'(?:[^'\\]|\\.)*'", TokenType.STRING),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
            
            # Operators (two-character first)
            (r'==', TokenType.EQ),
            (r'!=', TokenType.NEQ),
            (r'<=', TokenType.LTE),
            (r'>=', TokenType.GTE),
            (r'=', TokenType.ASSIGN), # Single-character = after ==
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'%', TokenType.MODULO),
            (r'<', TokenType.LT),
            (r'>', TokenType.GT),
            
            # Delimiters
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            (r',', TokenType.COMMA),  # NEW
            
            # Special
            (r'\n', TokenType.NEWLINE),
        ]
    
    def current_char(self) -> Optional[str]:
        """Returns current character or None if end reached"""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Looks ahead at character without moving position"""
        peek_pos = self.position + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self) -> None:
        """Moves to next character"""
        if self.position < len(self.source):
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def skip_whitespace(self) -> None:
        """Skips spaces and tabs (but not newlines)"""
        while (self.current_char() is not None and 
               self.current_char() in ' \t\r'):
            self.advance()
    
    def skip_comment(self) -> None:
        """Skips comments starting with #"""
        if self.current_char() == '#':
            # Skip until end of line
            while (self.current_char() is not None and 
                   self.current_char() != '\n'):
                self.advance()
    def tokenize(self) -> List[Token]:
        """
        Main tokenization method
        
        Returns:
            List[Token]: List of tokens
            
        Raises:
            LexerError: On lexical analysis errors
        """
        self.tokens = []
        
        while self.position < len(self.source):
            self.skip_whitespace()
            
            # End of file
            if self.current_char() is None:
                break
            
            # Comments
            if self.current_char() == '#':
                self.skip_comment()
                continue
            
            # Save current position for token
            token_line = self.line
            token_column = self.column
            # Try to find match with regular expressions
            found_match = False
            remaining_source = self.source[self.position:]
            
            for pattern, token_type in self.token_patterns:
                match = re.match(pattern, remaining_source)
                if match:
                    token_value = match.group(0)
                    self.tokens.append(Token(token_type, token_value, token_line, token_column))
                    
                    # Move position
                    for _ in range(len(token_value)):
                        self.advance()
                    
                    found_match = True
                    break
            
            if not found_match:
                # Unknown character
                unknown_char = self.current_char()
                raise LexerError(
                    f"Unknown character '{unknown_char}'",
                    self.line, self.column
                )
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
    
    def print_tokens(self) -> None:
        """Pretty prints all tokens for debugging"""
        print("=== TOKENS ===")
        for i, token in enumerate(self.tokens):
            print(f"{i:2}: {token}")


# Module testing
if __name__ == "__main__":
    # Test code with new features
    test_code = '''
# Comment - test logical operators
say "Hello, DoroLang!"
kas x = 42
kas y = (x + 10) % 3

# Test boolean values and logical operators
kas is_big = x > 30
kas is_small = y < 5
kas result = is_big and is_small

if (result) {
    say "Both conditions are true!"
} else {
    say "At least one condition is false"
}

# Test not operator
kas negative_result = not result
say "Negative result: " + negative_result

# Test or operator
if (is_big or is_small) {
    say "At least one is true"
}
'''

    # More detailed test for strings to ensure nothing broke
    string_test_code = '''
say "simple string"
say 'and in single quotes'
say "string with \\"escaped quote\\""
say 'and in single \\'too\\''
say "empty string: """
kas my_string="stringwithoutspace"
'''

    input_test_code = '''
# Test new input function
kas user_name = input("What is your name? ")
say "Hello, " + user_name + "!"
'''

    def run_lexer_test(name, code):
        """Helper function to run tests and output results"""
        print(f"\n===== RUNNING TEST: {name} =====")
        print("Source code:")
        print(code)
        print("-" * 20)
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            lexer.print_tokens()
            print(f"\n✅ Test '{name}' passed! Found {len(tokens)} tokens.")
        except LexerError as e:
            print(f"❌ Lexer error in test '{name}': {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    
    print("="*20 + " LEXER TESTING " + "="*20)

    # Run both tests
    run_lexer_test("Logical Operators", test_code)
    run_lexer_test("String Parsing", string_test_code)
    run_lexer_test("Input Function", input_test_code)

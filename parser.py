
"""
DoroLang Parser - Syntax Analyzer
Builds an Abstract Syntax Tree (AST) from tokens

Author: Dorofii Karnaukh
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

# Import tokens from lexer
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
    """Numeric literal: 42, 3.14"""
    value: float
    
    def __str__(self):
        return f"Number({self.value})"


@dataclass
class BooleanLiteral(Expression):
    """Boolean literal: true, false"""
    value: bool
    
    def __str__(self):
        return f"Boolean({self.value})"


@dataclass
class StringLiteral(Expression):
    """String literal: "hello", 'world'"""
    value: str
    
    def __str__(self):
        return f'String("{self.value}")'


@dataclass
class Identifier(Expression):
    """Variable identifier: name, age"""
    name: str
    
    def __str__(self):
        return f"Var({self.name})"


@dataclass
class BinaryOperation(Expression):
    """Binary operations: a + b, x * y, a and b"""
    left: Expression
    operator: str
    right: Expression
    
    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"


@dataclass
class UnaryOperation(Expression):
    """Unary operations: -x, +y, not condition"""
    operator: str
    operand: Expression
    
    def __str__(self):
        return f"({self.operator}{self.operand})"


@dataclass
class ParenthesizedExpression(Expression):
    expression: Expression

# New AST node for input
@dataclass
class InputCall(Expression):
    def __init__(self, prompt: Expression):
        self.prompt = prompt
    def __str__(self):
        return f"Input({self.prompt})"


@dataclass
class FunctionCall(Expression):
    """Function call: function_name(arg1, arg2, ...)"""
    name: str
    arguments: List[Expression]
    
    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"Call({self.name}({args_str}))"


# ============== STATEMENTS ==============

@dataclass
class SayStatement(Statement):
    """Say statement: say expression"""
    expression: Expression
    
    def __str__(self):
        return f"Say({self.expression})"


@dataclass
class AssignmentStatement(Statement):
    """Assignment: kas name = expression"""
    identifier: str
    expression: Expression
    
    def __str__(self):
        return f"Assign({self.identifier} = {self.expression})"


@dataclass
class BlockStatement(Statement):
    """Code block: { statement* }"""
    statements: List[Statement]
    
    def __str__(self):
        return f"Block({len(self.statements)} statements)"


@dataclass
class FunctionDefinition(Statement):
    """Function definition: function name(params) { ... }"""
    name: str
    parameters: List[str]
    body: BlockStatement
    
    def __str__(self):
        params_str = ", ".join(self.parameters)
        return f"Function({self.name}({params_str}))"


@dataclass
class ReturnStatement(Statement):
    """Return statement: return expression"""
    expression: Optional[Expression]
    
    def __str__(self):
        return f"Return({self.expression})"


@dataclass
class IfStatement(Statement):
    """If-Else statement"""
    condition: Expression
    then_branch: BlockStatement
    else_branch: Optional[Statement]  # Can be IfStatement or BlockStatement
    
    def __str__(self):
        else_info = " with else" if self.else_branch else ""
        return f"If({self.condition}){else_info}"


@dataclass
class WhileStatement(Statement):
    """While loop statement"""
    condition: Expression
    body: BlockStatement
    
    def __str__(self):
        return f"While({self.condition})"


@dataclass
class ForStatement(Statement):
    """For loop statement"""
    variable: str
    start: Expression
    end: Expression
    step: Optional[Expression]  # Optional step value
    body: BlockStatement
    
    def __str__(self):
        step_info = f", step {self.step}" if self.step else ""
        return f"For({self.variable} from {self.start} to {self.end}{step_info})"


@dataclass
class Program(ASTNode):
    """Program root - list of statements"""
    statements: List[Statement]
    
    def __str__(self):
        statements_str = "\n  ".join(str(stmt) for stmt in self.statements)
        return f"Program:\n  {statements_str}"


# ============== PARSER ==============

class ParseError(Exception):
    """Exception for parsing errors"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parse Error: {message} at line {token.line}:{token.column}")


class Parser:
    """
    Syntax analyzer for DoroLang
    
    Uses recursive descent to build AST
    Updated grammar (operator precedence):
    
    program         → statement*
    statement       → sayStatement | assignStatement | ifStatement | blockStatement
    blockStatement  → "{" statement* "}"
    ifStatement     → "if" "(" expression ")" statement ("else" statement)?
    sayStatement    → "say" expression
    assignStatement → "kas" IDENTIFIER "=" expression
    expression      → logicalOr
    logicalOr       → logicalAnd ("or" logicalAnd)*
    logicalAnd      → equality ("and" equality)*
    equality        → comparison (("==" | "!=") comparison)*
    comparison      → addition (("<" | ">" | "<=" | ">=") addition)*
    addition        → multiplication (("+" | "-") multiplication)*
    multiplication  → unary (("*" | "/" | "%") unary)*
    unary           → ("-" | "+" | "not") unary | primary
    primary         → NUMBER | STRING | BOOLEAN | IDENTIFIER | "(" expression ")"
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
    
    def current_token(self) -> Token:
        """Returns current token"""
        if self.position >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.position]
    
    def peek_token(self, offset: int = 1) -> Token:
        """Looks ahead at token"""
        peek_pos = self.position + offset
        if peek_pos >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[peek_pos]
    
    def advance(self) -> Token:
        """Moves to next token and returns previous"""
        current = self.current_token()
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return current
    
    def match(self, *expected_types: TokenType) -> bool:
        """Checks if current token matches any of expected types"""
        return self.current_token().type in expected_types
    
    def consume(self, expected_type: TokenType, error_message: str = "") -> Token:
        """Consumes token of expected type or raises error"""
        if self.match(expected_type):
            return self.advance()
        
        if not error_message:
            error_message = (f"Expected {expected_type.name}, "
                           f"got {self.current_token().type.name} '{self.current_token().value}'")
        
        raise ParseError(error_message, self.current_token())
    
    def skip_newlines(self) -> None:
        """Skips all newline tokens"""
        while self.match(TokenType.NEWLINE):
            self.advance()
    
    def parse(self) -> Program:
        """
        Main parsing method - parses entire program
        
        Returns:
            Program: Root AST node
            
        Raises:
            ParseError: On syntax errors
        """
        statements = []
        
        self.skip_newlines()  # Skip empty lines at start
        
        while not self.match(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue
            
            stmt = self.parse_statement()
            if stmt:  # Check that statement is not None
                statements.append(stmt)
        
        return Program(statements)
    
    def parse_statement(self) -> Optional[Statement]:
        """Parses one statement"""
        if self.match(TokenType.FUNCTION):
            return self.parse_function_definition()
        elif self.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.match(TokenType.WHILE):
            return self.parse_while_statement()
        elif self.match(TokenType.FOR):
            return self.parse_for_statement()
        elif self.match(TokenType.RETURN):
            return self.parse_return_statement()
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
        """Parses if-else statement. Parentheses around condition are optional."""
        self.consume(TokenType.IF, "Expected 'if'")

        # Condition is now parsed directly.
        # Pratt parser will handle parentheses if present,
        # as '(' is a prefix operator.
        condition = self.parse_expression()

        then_branch = self.parse_block_statement()

        else_branch = None
        if self.match(TokenType.ELSE):
            self.consume(TokenType.ELSE) # Consume 'else'
            # What comes after 'else' is just another statement
            # (can be a block {...} or another if)
            else_branch = self.parse_statement()
        return IfStatement(condition, then_branch, else_branch)
    
    def parse_while_statement(self) -> WhileStatement:
        """Parses while loop statement"""
        self.consume(TokenType.WHILE, "Expected 'while'")
        condition = self.parse_expression()
        body = self.parse_block_statement()
        return WhileStatement(condition, body)
    
    def parse_for_statement(self) -> ForStatement:
        """Parses for loop statement: for kas i = 1 to 10 { ... }"""
        self.consume(TokenType.FOR, "Expected 'for'")
        self.consume(TokenType.KAS, "Expected 'kas' after 'for'")
        
        # Get variable name
        var_token = self.consume(TokenType.IDENTIFIER, "Expected variable name after 'kas'")
        variable_name = var_token.value
        
        # Consume '='
        self.consume(TokenType.ASSIGN, "Expected '=' after variable name")
        
        # Parse start value
        start = self.parse_expression()
        
        # Consume 'to'
        if not (self.match(TokenType.IDENTIFIER) and self.current_token().value == 'to'):
            raise ParseError("Expected 'to' after start value", self.current_token())
        self.advance()
        
        # Parse end value
        end = self.parse_expression()
        
        # Optional step (step 2)
        step = None
        if self.match(TokenType.IDENTIFIER) and self.current_token().value == 'step':
            self.advance()
            step = self.parse_expression()
        
        # Parse body
        body = self.parse_block_statement()
        
        return ForStatement(variable_name, start, end, step, body)
    
    def parse_function_definition(self) -> FunctionDefinition:
        """Parses function definition: function name(param1, param2) { ... }"""
        self.consume(TokenType.FUNCTION, "Expected 'function'")
        
        # Get function name
        name_token = self.consume(TokenType.IDENTIFIER, "Expected function name")
        function_name = name_token.value
        
        # Parse parameters
        self.consume(TokenType.LPAREN, "Expected '(' after function name")
        parameters = []
        
        if not self.match(TokenType.RPAREN):
            while True:
                param_token = self.consume(TokenType.IDENTIFIER, "Expected parameter name")
                parameters.append(param_token.value)
                
                if self.match(TokenType.RPAREN):
                    break
                if self.match(TokenType.COMMA):
                    self.advance()
                else:
                    break
        
        self.consume(TokenType.RPAREN, "Expected ')' after parameters")
        
        # Parse function body
        body = self.parse_block_statement()
        
        return FunctionDefinition(function_name, parameters, body)
    
    def parse_return_statement(self) -> ReturnStatement:
        """Parses return statement"""
        self.consume(TokenType.RETURN, "Expected 'return'")
        
        # Check if return has no value (followed by newline or closing brace)
        if self.match(TokenType.NEWLINE) or self.match(TokenType.RBRACE) or self.match(TokenType.EOF):
            return ReturnStatement(None)
        
        expression = self.parse_expression()
        return ReturnStatement(expression)


    def parse_block_statement(self) -> BlockStatement:
        """Parses code block: { ... }"""
        self.consume(TokenType.LBRACE)
        self.skip_newlines()  # Allow newlines after '{'
        
        statements = []
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            statements.append(self.parse_statement())
            self.skip_newlines()  # Allow newlines after each statement
            
        self.consume(TokenType.RBRACE, "Expected '}' to close block")
        return BlockStatement(statements)

    def parse_say_statement(self) -> SayStatement:
        """Parses say statement"""
        self.consume(TokenType.SAY)  # Consume 'say'
        expression = self.parse_expression()  # Parse expression for output
        return SayStatement(expression)
    
    def parse_assignment_statement(self) -> AssignmentStatement:
        """Parses assignment: kas name = expression"""
        self.consume(TokenType.KAS)  # Consume 'kas'
        
        # Get variable name
        identifier_token = self.consume(
            TokenType.IDENTIFIER, 
            "Expected variable name after 'kas'"
        )
        identifier_name = identifier_token.value
        
        # Consume assignment sign
        self.consume(TokenType.ASSIGN, "Expected '=' after variable name")
        
        # Parse expression on the right of =
        expression = self.parse_expression()
        
        return AssignmentStatement(identifier_name, expression)
    
    def parse_expression(self) -> Expression:
        """Parses expression (entry point to precedence hierarchy)"""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> Expression:
        """Parses logical OR (lowest precedence)"""
        left = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            operator = self.advance().value
            right = self.parse_logical_and()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_logical_and(self) -> Expression:
        """Parses logical AND"""
        left = self.parse_equality()
        
        while self.match(TokenType.AND):
            operator = self.advance().value
            right = self.parse_equality()
            left = BinaryOperation(left, operator, right)
        
        return left

    def parse_equality(self) -> Expression:
        """Parses equality operators"""
        left = self.parse_comparison()
        
        while self.match(TokenType.EQ, TokenType.NEQ):
            operator = self.advance().value
            right = self.parse_comparison()
            left = BinaryOperation(left, operator, right)
            
        return left

    def parse_comparison(self) -> Expression:
        """Parses comparison operators"""
        left = self.parse_addition()
        
        while self.match(TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            operator = self.advance().value
            right = self.parse_addition()
            left = BinaryOperation(left, operator, right)
            
        return left
    
    def parse_addition(self) -> Expression:
        """Parses addition and subtraction"""
        left = self.parse_multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.advance().value
            right = self.parse_multiplication()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_multiplication(self) -> Expression:
        """Parses multiplication, division and modulo"""
        left = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.advance().value
            right = self.parse_unary()
            left = BinaryOperation(left, operator, right)
        
        return left
    
    def parse_unary(self) -> Expression:
        """Parses unary operations (including logical NOT)"""
        if self.match(TokenType.MINUS, TokenType.PLUS, TokenType.NOT):
            operator = self.advance().value
            operand = self.parse_unary()  # Recursive call to support --x and not not x
            return UnaryOperation(operator, operand)
        
        return self.parse_primary()
    
    def parse_primary(self) -> Expression:
        """Parses primary expressions"""
        # input("...")
        if self.match(TokenType.INPUT):
            self.advance()  # consume 'input'
            self.consume(TokenType.LPAREN, "Expected '(' after input")
            # Check if there's an expression inside parentheses
            if self.match(TokenType.RPAREN):
                self.advance()  # consume ')'
                # Empty prompt
                return InputCall(StringLiteral("") )
            else:
                prompt_expr = self.parse_expression()
                self.consume(TokenType.RPAREN, "Expected ')' after input prompt")
                return InputCall(prompt_expr)

        # Parentheses
        if self.match(TokenType.LPAREN):
            self.advance()  # consume '('
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return ParenthesizedExpression(expr)

        # Numbers
        elif self.match(TokenType.NUMBER):
            token = self.advance()
            return NumberLiteral(float(token.value))

        # Strings
        elif self.match(TokenType.STRING):
            token = self.advance()
            # Process string literal (remove quotes and handle escape)
            string_value = self._process_string_literal(token.value)
            return StringLiteral(string_value)

        # Boolean values
        elif self.match(TokenType.TRUE):
            self.advance()
            return BooleanLiteral(True)

        elif self.match(TokenType.FALSE):
            self.advance()
            return BooleanLiteral(False)

        # Identifiers (variables or function calls)
        elif self.match(TokenType.IDENTIFIER):
            token = self.advance()
            identifier_name = token.value
            
            # Check if it's a function call
            if self.match(TokenType.LPAREN):
                self.advance()  # consume '('
                arguments = []
                
                if not self.match(TokenType.RPAREN):
                    while True:
                        arguments.append(self.parse_expression())
                        if self.match(TokenType.RPAREN):
                            break
                        # Check for comma
                        if self.match(TokenType.COMMA):
                            self.advance()
                        else:
                            break
                
                self.consume(TokenType.RPAREN, "Expected ')' after function arguments")
                return FunctionCall(identifier_name, arguments)
            else:
                # Regular variable
                return Identifier(identifier_name)

        else:
            raise ParseError(
                f"Unexpected token in expression: '{self.current_token().value}'", 
                self.current_token()
            )
    
    def _process_string_literal(self, raw_string: str) -> str:
        """Processes string literal (removes quotes and handles escape sequences)"""
        # Remove outer quotes
        content = raw_string[1:-1]
        
        # Simple escape sequence handling
        content = content.replace('\\n', '\n')
        content = content.replace('\\t', '\t')
        content = content.replace('\\r', '\r')
        content = content.replace('\\\\', '\\')
        content = content.replace('\\"', '"')
        content = content.replace("\\'", "'")
        
        return content
    
    def pretty_print_ast(self, node: ASTNode, indent: int = 0) -> None:
        """Pretty prints AST tree"""
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
        
        elif isinstance(node, IfStatement):
            print(f"{prefix}IfStatement:")
            print(f"{prefix}  Condition:")
            self.pretty_print_ast(node.condition, indent + 2)
            print(f"{prefix}  Then:")
            self.pretty_print_ast(node.then_branch, indent + 2)
            if node.else_branch:
                print(f"{prefix}  Else:")
                self.pretty_print_ast(node.else_branch, indent + 2)
        
        elif isinstance(node, WhileStatement):
            print(f"{prefix}WhileStatement:")
            print(f"{prefix}  Condition:")
            self.pretty_print_ast(node.condition, indent + 2)
            print(f"{prefix}  Body:")
            self.pretty_print_ast(node.body, indent + 2)
        
        elif isinstance(node, ForStatement):
            print(f"{prefix}ForStatement: {node.variable}")
            print(f"{prefix}  Start:")
            self.pretty_print_ast(node.start, indent + 2)
            print(f"{prefix}  End:")
            self.pretty_print_ast(node.end, indent + 2)
            if node.step:
                print(f"{prefix}  Step:")
                self.pretty_print_ast(node.step, indent + 2)
            print(f"{prefix}  Body:")
            self.pretty_print_ast(node.body, indent + 2)
        
        elif isinstance(node, BlockStatement):
            print(f"{prefix}Block:")
            for stmt in node.statements:
                self.pretty_print_ast(stmt, indent + 1)
        
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
        
        elif isinstance(node, BooleanLiteral):
            print(f"{prefix}Boolean: {node.value}")
        
        elif isinstance(node, Identifier):
            print(f"{prefix}Variable: {node.name}")


# Module testing
if __name__ == "__main__":
    from lexer import Lexer
    
    # Test code with new features
    test_code = '''
say "Enhanced Parser test!"
kas x = 5
kas y = 3
kas z = true

# Test logical operators
kas result1 = x > y and z
kas result2 = x < y or not z
kas complex = (x + y) > 5 and (not z or y == 3)

say "result1 = " + result1
say "result2 = " + result2
say "complex = " + complex

# Test if-else with logical expressions
if (x > y and z) {
    say "Both conditions are true!"
    kas message = "Success!"
} else {
    say "Conditions not met"
    kas message = "Failed"
}

# Nested if-else
if (x > 10) {
    say "x is big"
} else {
    if (x > 3) {
        say "x is medium"  
    } else {
        say "x is small"
    }
}
'''
    
    print("=== TESTING ENHANCED PARSER ===")
    print("Source code:")
    print(test_code)
    print("\n" + "="*40)
    
    try:
        # Tokenization
        lexer = Lexer(test_code)
        tokens = lexer.tokenize()
        print(f"✅ Lexer: {len(tokens)} tokens")
        
        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()
        print(f"✅ Parser: {len(ast.statements)} statements")
        
        print("\n=== AST ===")
        parser.pretty_print_ast(ast)
        
        print("\n✅ Enhanced Parser test passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
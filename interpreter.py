# --- DoroLang input function (can be overridden in IDE) ---
def dorolang_input(prompt: str) -> str:
    return input(prompt)
"""
DoroLang Interpreter
Executes DoroLang programs by traversing the AST

Author: Dorofii Karnaukh
"""

from typing import Any, Dict, List
from parser import ( # noqa: E402
    ASTNode, Expression, Statement, Program,
    NumberLiteral, StringLiteral, BooleanLiteral, Identifier, InputCall,
    BinaryOperation, UnaryOperation, ParenthesizedExpression,
    SayStatement, AssignmentStatement, IfStatement, BlockStatement,
    WhileStatement, ForStatement, FunctionDefinition, FunctionCall, ReturnStatement,
)


class RuntimeError(Exception):
    """Runtime exception"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class Environment:
    """
    Environment for storing variables
    Can be extended in the future to support scopes
    """
    
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, FunctionDefinition] = {}  # NEW: Store functions
    
    def define(self, name: str, value: Any) -> None:
        """Defines a new variable"""
        self.variables[name] = value
    
    def get(self, name: str) -> Any:
        """Gets variable value"""
        if name not in self.variables:
            raise RuntimeError(f"Undefined variable: '{name}'")
        return self.variables[name]
    
    def set(self, name: str, value: Any) -> None:
        """Sets variable value"""
        self.variables[name] = value
    
    def define_function(self, name: str, function: FunctionDefinition) -> None:
        """Defines a function"""
        self.functions[name] = function
    
    def get_function(self, name: str) -> FunctionDefinition:
        """Gets function definition"""
        if name not in self.functions:
            raise RuntimeError(f"Undefined function: '{name}'")
        return self.functions[name]
    
    def clear(self) -> None:
        """Clears all variables and functions"""
        self.variables.clear()
        self.functions.clear()
    
    def __str__(self) -> str:
        """String representation of environment"""
        if not self.variables and not self.functions:
            return "Environment: (empty)"
        
        vars_str = ", ".join(f"{name}={value}" for name, value in self.variables.items())
        funcs_str = ", ".join(self.functions.keys())
        return f"Environment: vars=[{vars_str}], funcs=[{funcs_str}]"


class Interpreter:
    """
    DoroLang Interpreter
    
    Executes programs by traversing AST and evaluating nodes
    """
    
    def __init__(self):
        self.environment = Environment()
        self.output: List[str] = []  # For storing program output
        self.return_value: Any = None  # NEW: For return statements
        self.should_return: bool = False  # NEW: Flag for return
    
    def interpret(self, program: Program) -> List[str]:
        """
        Interprets a program
        
        Args:
            program: Root AST node of the program
            
        Returns:
            List[str]: All program output
            
        Raises:
            RuntimeError: On runtime errors
        """
        self.output = []
        
        try:
            for statement in program.statements:
                self.execute_statement(statement)
        except RuntimeError as e:
            error_msg = f"❌ Runtime error: {e.message}"
            print(error_msg)
            self.output.append(error_msg)
        
        return self.output
    
    def execute_statement(self, statement: Statement) -> None:
        """Executes a statement"""
        if isinstance(statement, FunctionDefinition):
            self.execute_function_definition(statement)
        elif isinstance(statement, IfStatement):
            self.execute_if_statement(statement)
        elif isinstance(statement, WhileStatement):
            self.execute_while_statement(statement)
        elif isinstance(statement, ForStatement):
            self.execute_for_statement(statement)
        elif isinstance(statement, SayStatement):
            self.execute_say_statement(statement)
        elif isinstance(statement, AssignmentStatement):
            self.execute_assignment_statement(statement)
        elif isinstance(statement, BlockStatement):
            self.execute_block_statement(statement)
        elif isinstance(statement, ReturnStatement):
            self.execute_return_statement(statement)
        else:
            raise RuntimeError(f"Unknown statement type: {type(statement).__name__}")
    
    def execute_say_statement(self, statement: SayStatement) -> None:
        """Executes say statement"""
        value = self.evaluate_expression(statement.expression)
        output_line = str(value)
        print(output_line)
        self.output.append(output_line)
    
    def execute_assignment_statement(self, statement: AssignmentStatement) -> None:
        """Executes assignment"""
        value = self.evaluate_expression(statement.expression)
        self.environment.set(statement.identifier, value)

    def execute_if_statement(self, statement: IfStatement) -> None:
        """Executes if-else statement"""
        condition_value = self.evaluate_expression(statement.condition)
        if self._is_truthy(condition_value):
            self.execute_statement(statement.then_branch)
        elif statement.else_branch is not None:
            self.execute_statement(statement.else_branch)

    def execute_block_statement(self, statement: BlockStatement) -> None:
        """Executes a code block"""
        # In the future, a new scope can be created here
        for stmt in statement.statements:
            if self.should_return:
                break
            self.execute_statement(stmt)
    
    def execute_while_statement(self, statement: WhileStatement) -> None:
        """Executes while loop"""
        while self._is_truthy(self.evaluate_expression(statement.condition)):
            self.execute_statement(statement.body)
    
    def execute_for_statement(self, statement: ForStatement) -> None:
        """Executes for loop"""
        start_val = self.evaluate_expression(statement.start)
        end_val = self.evaluate_expression(statement.end)
        step_val = self.evaluate_expression(statement.step) if statement.step else 1
        
        # Convert to numbers
        start_num = self._to_numeric(start_val)
        end_num = self._to_numeric(end_val)
        step_num = self._to_numeric(step_val)
        
        if not isinstance(start_num, (int, float)) or not isinstance(end_num, (int, float)) or not isinstance(step_num, (int, float)):
            raise RuntimeError("For loop requires numeric values for start, end, and step")
        
        # Set initial value
        self.environment.set(statement.variable, start_num)
        
        # Determine direction
        if step_num > 0:
            # Counting up
            while start_num <= end_num:
                self.execute_statement(statement.body)
                start_num += step_num
                self.environment.set(statement.variable, start_num)
        elif step_num < 0:
            # Counting down
            while start_num >= end_num:
                self.execute_statement(statement.body)
                start_num += step_num
                self.environment.set(statement.variable, start_num)
        else:
            raise RuntimeError("For loop step cannot be zero")
    
    def execute_function_definition(self, statement: FunctionDefinition) -> None:
        """Defines a function"""
        self.environment.define_function(statement.name, statement)
    
    def execute_return_statement(self, statement: ReturnStatement) -> None:
        """Executes return statement"""
        if statement.expression:
            self.return_value = self.evaluate_expression(statement.expression)
        else:
            self.return_value = None
        self.should_return = True
    
    def call_function(self, name: str, arguments: List[Expression]) -> Any:
        """Calls a function with arguments"""
        function = self.environment.get_function(name)
        
        # Check argument count
        if len(arguments) != len(function.parameters):
            raise RuntimeError(
                f"Function '{name}' expects {len(function.parameters)} arguments, "
                f"but got {len(arguments)}"
            )
        
        # Save current environment state
        old_variables = self.environment.variables.copy()
        
        # Create new scope for function parameters
        for param, arg_expr in zip(function.parameters, arguments):
            arg_value = self.evaluate_expression(arg_expr)
            self.environment.define(param, arg_value)
        
        # Reset return flags
        self.should_return = False
        self.return_value = None
        
        # Execute function body
        self.execute_statement(function.body)
        
        # Get return value
        result = self.return_value
        
        # Restore environment
        self.environment.variables = old_variables
        self.should_return = False
        
        return result

    
    def evaluate_expression(self, expression: Expression) -> Any:
        """
        Evaluates an expression
        
        Args:
            expression: AST expression node
            
        Returns:
            Any: Expression value
            
        Raises:
            RuntimeError: On evaluation errors
        """
        if isinstance(expression, NumberLiteral):
            return expression.value
        
        elif isinstance(expression, StringLiteral):
            return expression.value
        
        elif isinstance(expression, BooleanLiteral):
            return expression.value
        
        elif isinstance(expression, Identifier):
            return self.environment.get(expression.name)
        
        elif isinstance(expression, BinaryOperation):
            left_val = self.evaluate_expression(expression.left)
            right_val = self.evaluate_expression(expression.right)
            return self.apply_binary_operation(left_val, expression.operator, right_val)
        
        elif isinstance(expression, UnaryOperation):
            operand_val = self.evaluate_expression(expression.operand)
            return self.apply_unary_operation(expression.operator, operand_val)
        
        elif isinstance(expression, ParenthesizedExpression):
            return self.evaluate_expression(expression.expression)

        # New: input() handling
        elif isinstance(expression, InputCall):
            prompt = self.evaluate_expression(expression.prompt)
            return dorolang_input(str(prompt))
        
        # Function call handling
        elif isinstance(expression, FunctionCall):
            return self.call_function(expression.name, expression.arguments)

        raise RuntimeError(f"Unknown expression type: {type(expression).__name__}")
    
    def _to_numeric(self, value: Any) -> Any:
        """
        Attempts to convert a string value to a number (int or float).
        If conversion is not possible, returns the original value.
        """
        if isinstance(value, str):
            try:
                if '.' in value:
                    return float(value)
                return int(value)
            except (ValueError, TypeError):
                return value
        return value

    def apply_binary_operation(self, left: Any, operator: str, right: Any) -> Any:
        """
        Applies a binary operation
        
        Args:
            left: Left operand
            operator: Operator (+, -, *, /, %, ==, !=, <, >, <=, >=, and, or)
            right: Right operand
            
        Returns:
            Any: Operation result
            
        Raises:
            RuntimeError: On incompatible types or other errors
        """
        
        # Logical operators (new)
        if operator == 'and':
            return self._is_truthy(left) and self._is_truthy(right)
        elif operator == 'or':
            return self._is_truthy(left) or self._is_truthy(right)
        
        # Attempt to convert operands to numbers for arithmetic and comparison operations
        num_left = self._to_numeric(left)
        num_right = self._to_numeric(right)

        # Addition: numeric if possible, otherwise concatenation
        if operator == '+':
            if isinstance(num_left, (int, float)) and isinstance(num_right, (int, float)):
                return num_left + num_right
            
            # Otherwise - string concatenation. Convert booleans to 'true'/'false'.
            s_left = str(left).lower() if isinstance(left, bool) else str(left)
            s_right = str(right).lower() if isinstance(right, bool) else str(right)
            return s_left + s_right

        # Other arithmetic operations (require numbers)
        elif operator in ['-', '*', '/', '%']:
            if not isinstance(num_left, (int, float)) or not isinstance(num_right, (int, float)):
                raise RuntimeError(
                    f"Cannot apply '{operator}' to non-numeric values ('{left}' and '{right}')"
                )
            
            if operator == '-':
                return num_left - num_right
            elif operator == '*':
                return num_left * num_right
            elif operator == '/':
                if num_right == 0:
                    raise RuntimeError("Division by zero")
                return num_left / num_right
            elif operator == '%':
                if num_right == 0:
                    raise RuntimeError("Modulo by zero")
                return num_left % num_right
        
        # Comparison operators
        elif operator in ['==', '!=', '<', '>', '<=', '>=']:
            # Use already converted numeric values if possible
            l, r = num_left, num_right

            # If both are numbers - compare as numbers
            if isinstance(l, (int, float)) and isinstance(r, (int, float)):
                if operator == '==': return l == r
                if operator == '!=': return l != r
                if operator == '<': return l < r
                if operator == '>': return l > r
                if operator == '<=': return l <= r
                if operator == '>=': return l >= r
            # If both are strings - compare as strings
            elif isinstance(l, str) and isinstance(r, str):
                if operator == '==': return l == r
                if operator == '!=': return l != r
                if operator == '<': return l < r
                if operator == '>': return l > r
                if operator == '<=': return l <= r
                if operator == '>=': return l >= r
            # If both are booleans - compare as booleans
            elif isinstance(l, bool) and isinstance(r, bool):
                if operator == '==': return l == r
                if operator == '!=': return l != r
                if operator == '<': return l < r
                if operator == '>': return l > r
                if operator == '<=': return l <= r
                if operator == '>=': return l >= r
            else:
                # By default, unequal types are not equal for '==' and '!='
                if operator == '==': return False
                if operator == '!=': return True
                # For other operators - error
                raise RuntimeError(f"Cannot compare {type(left).__name__} and {type(right).__name__} with '{operator}'")

    def apply_unary_operation(self, operator: str, operand: Any) -> Any:
        """Applies a unary operation"""
        if operator == 'not':
            # Logical NOT - works with any type
            return not self._is_truthy(operand)

        # For unary + and - attempt to convert operand to number
        num_operand = self._to_numeric(operand)

        if not isinstance(num_operand, (int, float)):
            raise RuntimeError(
                f"Cannot apply unary '{operator}' to non-numeric value '{operand}'"
            )

        if operator == '-':
            return -num_operand
        elif operator == '+':
            return num_operand
        
        raise RuntimeError(f"Unknown unary operator: '{operator}'")
    
    def _is_truthy(self, value: Any) -> bool:
        """
        Checks value for 'truthiness'.
        Truthiness rules in DoroLang:
        - false -> False
        - true -> True
        - 0 (number) -> False
        - any other number -> True
        - "" (empty string) -> False
        - any other string -> True
        - None -> False
        """
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)) and value == 0:
            return False
        if isinstance(value, str) and value == "":
            return False
        return True

    def reset(self) -> None:
        """Resets interpreter state"""
        self.environment.clear()
        self.output = []
        self.return_value = None
        self.should_return = False
    
    def get_variables(self) -> Dict[str, Any]:
        """Returns current variables"""
        return self.environment.variables.copy()
    
    def set_variable(self, name: str, value: Any) -> None:
        """Sets a variable (for interactive mode)"""
        self.environment.set(name, value)


# Module testing
if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    
    # Test code with new features
    test_code = '''
say "Enhanced Interpreter test!"

# Test boolean values
kas is_true = true
kas is_false = false
say "is_true = " + is_true
say "is_false = " + is_false

# Test logical operators
kas x = 10
kas y = 5
kas result_and = x > 5 and y < 10
kas result_or = x < 5 or y < 10
kas result_not = not is_false

say "x > 5 and y < 10 = " + result_and
say "x < 5 or y < 10 = " + result_or  
say "not false = " + result_not

# Test if-else with logical expressions
if (x > y and is_true) {
    say "Complex condition is true!"
    kas status = "success"
} else {
    say "Complex condition is false"
    kas status = "failed"
}

# Test nested conditionals
if (x > 15) {
    say "x is very big"
} else {
    if (x > 8) {
        say "x is big enough"
    } else {
        say "x is too small"
    }
}

# Test complex logical expressions
kas complex_result = (x + y) > 10 and not is_false or y == 5
say "Complex logical result: " + complex_result

# Test truthiness of various types
kas empty_string = ""
kas non_empty_string = "hello"
kas zero = 0
kas non_zero = 42

say "Empty string is truthy: " + (not not empty_string)
say "Non-empty string is truthy: " + (not not non_empty_string)
say "Zero is truthy: " + (not not zero)
say "Non-zero is truthy: " + (not not non_zero)
'''
    
    print("=== TESTING ENHANCED INTERPRETER ===")
    print("Source code:")
    print(test_code)
    print("\n" + "="*40)
    
    try:
        # Full cycle: lexer -> parser -> interpreter
        lexer = Lexer(test_code)
        tokens = lexer.tokenize()
        print(f"✅ Lexer: {len(tokens)} tokens")
        
        parser = Parser(tokens)
        ast = parser.parse()
        print(f"✅ Parser: {len(ast.statements)} statements")
        
        interpreter = Interpreter()
        output = interpreter.interpret(ast)
        print(f"✅ Interpreter: executed successfully")
        
        print("\n=== VARIABLES ===")
        variables = interpreter.get_variables()
        for name, value in variables.items():
            print(f"  {name} = {value} ({type(value).__name__})")
        
        print(f"\n=== OUTPUT SUMMARY ===")
        print(f"Total output lines: {len(output)}")
        
        print("\n✅ Enhanced Interpreter test passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
"""
DoroLang Interpreter - Интерпретатор
Выполняет программы DoroLang, обходя AST

Автор: Dorofii Karnaukh
"""

from typing import Any, Dict, List
from parser import (
    ASTNode, Expression, Statement, Program,
    NumberLiteral, StringLiteral, Identifier,
    BinaryOperation, UnaryOperation, ParenthesizedExpression,
    SayStatement, AssignmentStatement
)


class RuntimeError(Exception):
    """Исключение времени выполнения"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class Environment:
    """
    Окружение для хранения переменных
    В будущем можно расширить для поддержки областей видимости
    """
    
    def __init__(self):
        self.variables: Dict[str, Any] = {}
    
    def define(self, name: str, value: Any) -> None:
        """Определяет новую переменную"""
        self.variables[name] = value
    
    def get(self, name: str) -> Any:
        """Получает значение переменной"""
        if name not in self.variables:
            raise RuntimeError(f"Undefined variable: '{name}'")
        return self.variables[name]
    
    def set(self, name: str, value: Any) -> None:
        """Устанавливает значение переменной"""
        self.variables[name] = value
    
    def clear(self) -> None:
        """Очищает все переменные"""
        self.variables.clear()
    
    def __str__(self) -> str:
        """Строковое представление окружения"""
        if not self.variables:
            return "Environment: (empty)"
        
        vars_str = ", ".join(f"{name}={value}" for name, value in self.variables.items())
        return f"Environment: {vars_str}"


class Interpreter:
    """
    Интерпретатор DoroLang
    
    Выполняет программы путем обхода AST и вычисления узлов
    """
    
    def __init__(self):
        self.environment = Environment()
        self.output: List[str] = []  # Для сохранения вывода программы
    
    def interpret(self, program: Program) -> List[str]:
        """
        Интерпретирует программу
        
        Args:
            program: Корневой узел AST программы
            
        Returns:
            List[str]: Весь вывод программы
            
        Raises:
            RuntimeError: При ошибках времени выполнения
        """
        self.output = []
        
        for statement in program.statements:
            try:
                self.execute_statement(statement)
            except RuntimeError as e:
                error_msg = f"❌ Runtime error: {e.message}"
                print(error_msg)
                self.output.append(error_msg)
                # Продолжаем выполнение остальных утверждений
        
        return self.output
    
    def execute_statement(self, statement: Statement) -> None:
        """Выполняет утверждение"""
        if isinstance(statement, SayStatement):
            self.execute_say_statement(statement)
        elif isinstance(statement, AssignmentStatement):
            self.execute_assignment_statement(statement)
        else:
            raise RuntimeError(f"Unknown statement type: {type(statement).__name__}")
    
    def execute_say_statement(self, statement: SayStatement) -> None:
        """Выполняет say утверждение"""
        value = self.evaluate_expression(statement.expression)
        output_line = str(value)
        print(output_line)
        self.output.append(output_line)
    
    def execute_assignment_statement(self, statement: AssignmentStatement) -> None:
        """Выполняет присваивание"""
        value = self.evaluate_expression(statement.expression)
        self.environment.set(statement.identifier, value)
    
    def evaluate_expression(self, expression: Expression) -> Any:
        """
        Вычисляет выражение
        
        Args:
            expression: Узел выражения AST
            
        Returns:
            Any: Значение выражения
            
        Raises:
            RuntimeError: При ошибках вычисления
        """
        if isinstance(expression, NumberLiteral):
            return expression.value
        
        elif isinstance(expression, StringLiteral):
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
        
        else:
            raise RuntimeError(f"Unknown expression type: {type(expression).__name__}")
    
    def apply_binary_operation(self, left: Any, operator: str, right: Any) -> Any:
        """
        Применяет бинарную операцию
        
        Args:
            left: Левый операнд
            operator: Оператор (+, -, *, /, %)
            right: Правый операнд
            
        Returns:
            Any: Результат операции
            
        Raises:
            RuntimeError: При несовместимых типах или других ошибках
        """
        
        # Сложение
        if operator == '+':
            # Числа + числа
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            # Строки + строки
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            # Строка + число
            elif isinstance(left, str) and isinstance(right, (int, float)):
                return left + str(right)
            # Число + строка
            elif isinstance(left, (int, float)) and isinstance(right, str):
                return str(left) + right
            else:
                raise RuntimeError(
                    f"Cannot add {type(left).__name__} and {type(right).__name__}"
                )
        
        # Остальные арифметические операции (только для чисел)
        elif operator in ['-', '*', '/', '%']:
            if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
                raise RuntimeError(
                    f"Cannot apply '{operator}' to {type(left).__name__} and {type(right).__name__}"
                )
            
            if operator == '-':
                return left - right
            elif operator == '*':
                return left * right
            elif operator == '/':
                if right == 0:
                    raise RuntimeError("Division by zero")
                return left / right
            elif operator == '%':
                if right == 0:
                    raise RuntimeError("Modulo by zero")
                return left % right
        
        else:
            raise RuntimeError(f"Unknown binary operator: '{operator}'")
    
    def apply_unary_operation(self, operator: str, operand: Any) -> Any:
        """
        Применяет унарную операцию
        
        Args:
            operator: Унарный оператор (+ или -)
            operand: Операнд
            
        Returns:
            Any: Результат операции
            
        Raises:
            RuntimeError: При несовместимых типах
        """
        if operator == '-':
            if not isinstance(operand, (int, float)):
                raise RuntimeError(
                    f"Cannot apply unary minus to {type(operand).__name__}"
                )
            return -operand
        elif operator == '+':
            if not isinstance(operand, (int, float)):
                raise RuntimeError(
                    f"Cannot apply unary plus to {type(operand).__name__}"
                )
            return operand
        else:
            raise RuntimeError(f"Unknown unary operator: '{operator}'")
    
    def reset(self) -> None:
        """Сбрасывает состояние интерпретатора"""
        self.environment.clear()
        self.output = []
    
    def get_variables(self) -> Dict[str, Any]:
        """Возвращает текущие переменные"""
        return self.environment.variables.copy()
    
    def set_variable(self, name: str, value: Any) -> None:
        """Устанавливает переменную (для интерактивного режима)"""
        self.environment.set(name, value)


# Тестирование модуля
if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    
    # Тестовый код
    test_code = '''
say "Interpreter test!"
kas x = 10
kas y = 5
say "x = " + x
say "y = " + y
say "x + y = " + (x + y)
say "x - y = " + (x - y)
say "x * y = " + (x * y)
say "x / y = " + (x / y)
say "x % y = " + (x % y)

kas negative = -x
say "negative = " + negative

kas complex = (x + y) * 2 - negative
say "complex = " + complex

kas name = "DoroLang"
say "Language: " + name
'''
    
    print("=== TESTING INTERPRETER ===")
    print("Source code:")
    print(test_code)
    print("\n" + "="*40)
    
    try:
        # Полный цикл: лексер -> парсер -> интерпретатор
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
        
        print("\n✅ Interpreter test passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
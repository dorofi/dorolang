# --- DoroLang input function (может быть переопределена в IDE) ---
def dorolang_input(prompt: str) -> str:
    return input(prompt)
"""
DoroLang Interpreter - Интерпретатор
Выполняет программы DoroLang, обходя AST

Автор: Dorofii Karnaukh
"""

from typing import Any, Dict, List
from parser import ( # noqa: E402
    ASTNode, Expression, Statement, Program,
    NumberLiteral, StringLiteral, BooleanLiteral, Identifier, InputCall,
    BinaryOperation, UnaryOperation, ParenthesizedExpression,
    SayStatement, AssignmentStatement, IfStatement, BlockStatement,
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
        
        try:
            for statement in program.statements:
                self.execute_statement(statement)
        except RuntimeError as e:
            error_msg = f"❌ Runtime error: {e.message}"
            print(error_msg)
            self.output.append(error_msg)
        
        return self.output
    
    def execute_statement(self, statement: Statement) -> None:
        """Выполняет утверждение"""
        if isinstance(statement, IfStatement):
            self.execute_if_statement(statement)
        elif isinstance(statement, SayStatement):
            self.execute_say_statement(statement)
        elif isinstance(statement, AssignmentStatement):
            self.execute_assignment_statement(statement)
        elif isinstance(statement, BlockStatement):
            self.execute_block_statement(statement)
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

    def execute_if_statement(self, statement: IfStatement) -> None:
        """Выполняет if-else утверждение"""
        condition_value = self.evaluate_expression(statement.condition)
        if self._is_truthy(condition_value):
            self.execute_statement(statement.then_branch)
        elif statement.else_branch is not None:
            self.execute_statement(statement.else_branch)

    def execute_block_statement(self, statement: BlockStatement) -> None:
        """Выполняет блок кода"""
        # В будущем здесь можно будет создать новую область видимости
        for stmt in statement.statements:
            self.execute_statement(stmt)

    
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

        # Новый: обработка input()
        elif isinstance(expression, InputCall):
            prompt = self.evaluate_expression(expression.prompt)
            return dorolang_input(str(prompt))

        raise RuntimeError(f"Unknown expression type: {type(expression).__name__}")
    
    def _to_numeric(self, value: Any) -> Any:
        """
        Пытается преобразовать строковое значение в число (int или float).
        Если преобразование невозможно, возвращает исходное значение.
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
        Применяет бинарную операцию
        
        Args:
            left: Левый операнд
            operator: Оператор (+, -, *, /, %, ==, !=, <, >, <=, >=, and, or)
            right: Правый операнд
            
        Returns:
            Any: Результат операции
            
        Raises:
            RuntimeError: При несовместимых типах или других ошибках
        """
        
        # Логические операторы (новые)
        if operator == 'and':
            return self._is_truthy(left) and self._is_truthy(right)
        elif operator == 'or':
            return self._is_truthy(left) or self._is_truthy(right)
        
        # Попытка преобразовать операнды в числа для арифметических и сравнительных операций
        num_left = self._to_numeric(left)
        num_right = self._to_numeric(right)

        # Сложение: численное, если возможно, иначе конкатенация
        if operator == '+':
            if isinstance(num_left, (int, float)) and isinstance(num_right, (int, float)):
                return num_left + num_right
            
            # Иначе - конкатенация строк. Булевы значения конвертируем в 'true'/'false'.
            s_left = str(left).lower() if isinstance(left, bool) else str(left)
            s_right = str(right).lower() if isinstance(right, bool) else str(right)
            return s_left + s_right

        # Остальные арифметические операции (требуют числа)
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
        
        # Операторы сравнения
        elif operator in ['==', '!=', '<', '>', '<=', '>=']:
            # Используем уже преобразованные в числа значения, если это возможно
            l, r = num_left, num_right

            # Если оба числа — сравниваем как числа
            if isinstance(l, (int, float)) and isinstance(r, (int, float)):
                if operator == '==': return l == r
                if operator == '!=': return l != r
                if operator == '<': return l < r
                if operator == '>': return l > r
                if operator == '<=': return l <= r
                if operator == '>=': return l >= r
            # Если оба строки — сравниваем как строки
            elif isinstance(l, str) and isinstance(r, str):
                if operator == '==': return l == r
                if operator == '!=': return l != r
                if operator == '<': return l < r
                if operator == '>': return l > r
                if operator == '<=': return l <= r
                if operator == '>=': return l >= r
            # Если оба булевые — сравниваем как булевые
            elif isinstance(l, bool) and isinstance(r, bool):
                if operator == '==': return l == r
                if operator == '!=': return l != r
                if operator == '<': return l < r
                if operator == '>': return l > r
                if operator == '<=': return l <= r
                if operator == '>=': return l >= r
            else:
                # По умолчанию неравные типы не равны для '==' и '!='
                if operator == '==': return False
                if operator == '!=': return True
                # Для остальных операторов - ошибка
                raise RuntimeError(f"Cannot compare {type(left).__name__} and {type(right).__name__} with '{operator}'")

    def apply_unary_operation(self, operator: str, operand: Any) -> Any:
        """Применяет унарную операцию"""
        if operator == 'not':
            # Логический NOT - работает с любым типом
            return not self._is_truthy(operand)

        # Для унарных + и - пытаемся преобразовать операнд в число
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
        Проверяет значение на 'истинность'.
        Правила истинности в DoroLang:
        - false -> False
        - true -> True
        - 0 (число) -> False
        - любое другое число -> True
        - "" (пустая строка) -> False
        - любая другая строка -> True
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
    
    # Тестовый код с новыми возможностями
    test_code = '''
say "Enhanced Interpreter test!"

# Тест булевых значений
kas is_true = true
kas is_false = false
say "is_true = " + is_true
say "is_false = " + is_false

# Тест логических операторов
kas x = 10
kas y = 5
kas result_and = x > 5 and y < 10
kas result_or = x < 5 or y < 10
kas result_not = not is_false

say "x > 5 and y < 10 = " + result_and
say "x < 5 or y < 10 = " + result_or  
say "not false = " + result_not

# Тест if-else с логическими выражениями
if (x > y and is_true) {
    say "Complex condition is true!"
    kas status = "success"
} else {
    say "Complex condition is false"
    kas status = "failed"
}

# Тест вложенных условий
if (x > 15) {
    say "x is very big"
} else {
    if (x > 8) {
        say "x is big enough"
    } else {
        say "x is too small"
    }
}

# Тест сложных логических выражений
kas complex_result = (x + y) > 10 and not is_false or y == 5
say "Complex logical result: " + complex_result

# Тест истинности различных типов
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
        
        print("\n✅ Enhanced Interpreter test passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
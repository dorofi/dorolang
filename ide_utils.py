import os
import sys
import traceback

# Глобальная переменная для отслеживания инициализации
DOROLANG_MODULES_OK = False

# Попытка импорта модулей DoroLang с детальной диагностикой
def check_and_import_dorolang():
    """Проверка и импорт модулей DoroLang"""
    global DOROLANG_MODULES_OK
    
    try:
        print("Проверка модулей DoroLang...")
        
        required_files = ['lexer.py', 'parser.py', 'interpreter.py']
        missing_files = [file for file in required_files if not os.path.exists(file)]
        
        if missing_files:
            raise ImportError(f"Отсутствуют файлы: {', '.join(missing_files)}")
        
        from lexer import Lexer, LexerError
        from parser import Parser, ParseError
        from interpreter import Interpreter, RuntimeError as DoroRuntimeError
        
        DOROLANG_MODULES_OK = True
        print("✅ Все модули DoroLang успешно загружены!")
        
        return Lexer, LexerError, Parser, ParseError, Interpreter, DoroRuntimeError
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке модулей DoroLang: {e}")
        traceback.print_exc()
        return None, None, None, None, None, None


# Импортируем модули при загрузке
Lexer, LexerError, Parser, ParseError, Interpreter, DoroRuntimeError = check_and_import_dorolang()


class MockInterpreter:
    """Заглушка интерпретатора для демонстрации без DoroLang модулей"""
    
    def __init__(self):
        self.variables = {}
    
    def interpret(self, code):
        return [f"DEMO MODE: Получен код длиной {len(code)} символов"]
    
    def reset(self):
        self.variables = {}
    
    def get_variables(self):
        return self.variables.copy()


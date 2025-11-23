import os
import sys
import traceback

# Global variable for tracking initialization
DOROLANG_MODULES_OK = False

# Attempt to import DoroLang modules with detailed diagnostics
def check_and_import_dorolang():
    """Check and import DoroLang modules"""
    global DOROLANG_MODULES_OK
    
    try:
        print("Checking DoroLang modules...")
        
        required_files = ['lexer.py', 'parser.py', 'interpreter.py']
        missing_files = [file for file in required_files if not os.path.exists(file)]
        
        if missing_files:
            raise ImportError(f"Missing files: {', '.join(missing_files)}")
        
        from lexer import Lexer, LexerError
        from parser import Parser, ParseError
        from interpreter import Interpreter, RuntimeError as DoroRuntimeError
        
        DOROLANG_MODULES_OK = True
        print("✅ All DoroLang modules successfully loaded!")
        
        return Lexer, LexerError, Parser, ParseError, Interpreter, DoroRuntimeError
        
    except Exception as e:
        print(f"❌ Error loading DoroLang modules: {e}")
        traceback.print_exc()
        return None, None, None, None, None, None


# Import modules on load
Lexer, LexerError, Parser, ParseError, Interpreter, DoroRuntimeError = check_and_import_dorolang()


class MockInterpreter:
    """Mock interpreter for demonstration without DoroLang modules"""
    
    def __init__(self):
        self.variables = {}
    
    def interpret(self, code):
        return [f"DEMO MODE: Received code {len(code)} characters long"]
    
    def reset(self):
        self.variables = {}
    
    def get_variables(self):
        return self.variables.copy()


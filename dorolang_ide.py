#!/usr/bin/env python3
"""
DoroLang IDE - Интегрированная среда разработки (Улучшенная версия)
Полнофункциональная IDE для языка DoroLang с поддержкой новых возможностей

Автор: Dorofii Karnaukh
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import tkinter.scrolledtext as scrolledtext
import os
import sys
import threading
import io
import re
import json
import traceback

# Глобальная переменная для отслеживания инициализации
DOROLANG_MODULES_OK = False

# Попытка импорта модулей DoroLang с детальной диагностикой
def check_and_import_dorolang():
    """Проверка и импорт модулей DoroLang"""
    global DOROLANG_MODULES_OK
    
    try:
        print("Проверка модулей DoroLang...")
        
        # Проверяем наличие файлов
        required_files = ['lexer.py', 'parser.py', 'interpreter.py']
        missing_files = []
        
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
                print(f"❌ Файл не найден: {file}")
            else:
                print(f"✅ Файл найден: {file}")
        
        if missing_files:
            raise ImportError(f"Отсутствуют файлы: {', '.join(missing_files)}")
        
        # Пытаемся импортировать
        print("Импортирование модулей...")
        
        try:
            from lexer import Lexer, LexerError
            print("✅ lexer.py импортирован")
        except Exception as e:
            print(f"❌ Ошибка импорта lexer.py: {e}")
            raise
        
        try:
            from parser import Parser, ParseError
            print("✅ parser.py импортирован")
        except Exception as e:
            print(f"❌ Ошибка импорта parser.py: {e}")
            raise
        
        try:
            from interpreter import Interpreter, RuntimeError as DoroRuntimeError
            print("✅ interpreter.py импортирован")
        except Exception as e:
            print(f"❌ Ошибка импорта interpreter.py: {e}")
            raise
        
        DOROLANG_MODULES_OK = True
        print("✅ Все модули DoroLang успешно загружены!")
        
        # Возвращаем импортированные классы
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


class SyntaxHighlighter:
    """Улучшенная подсветка синтаксиса для DoroLang с поддержкой новых возможностей"""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.setup_tags()
        self.compile_regex()
        self.highlight_job = None

    def setup_tags(self):
        """Настройка тегов для подсветки"""
        try:
            # Ключевые слова
            self.text_widget.tag_config("keyword", foreground="#0066CC", font=("Consolas", 11, "bold"))
            # Логические операторы (новый стиль)
            self.text_widget.tag_config("logical", foreground="#9A4500", font=("Consolas", 11, "bold"))
            # Булевы значения
            self.text_widget.tag_config("boolean", foreground="#008B8B", font=("Consolas", 11, "bold"))
            # Строки
            self.text_widget.tag_config("string", foreground="#009900")
            # Числа
            self.text_widget.tag_config("number", foreground="#FF6600")
            # Комментарии
            self.text_widget.tag_config("comment", foreground="#808080", font=("Consolas", 11, "italic"))
            # Операторы
            self.text_widget.tag_config("operator", foreground="#CC0066")
            # Разделители
            self.text_widget.tag_config("delimiter", foreground="#666666")
        except Exception as e:
            print(f"Предупреждение: Ошибка настройки тегов подсветки: {e}")
    
    def compile_regex(self):
        """Компиляция регулярного выражения с поддержкой новых токенов"""
        keywords = ['say', 'kas', 'if', 'else']
        logical_ops = ['and', 'or', 'not']
        boolean_values = ['true', 'false']
        
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        logical_pattern = r'\b(' + '|'.join(logical_ops) + r')\b'
        boolean_pattern = r'\b(' + '|'.join(boolean_values) + r')\b'

        # Порядок важен!
        token_patterns = [
            ('COMMENT', r'#.*$'),
            ('STRING', r'(".*?"|\'.*?\')'),
            ('NUMBER', r'\b\d+\.?\d*\b'),
            ('BOOLEAN', boolean_pattern),
            ('LOGICAL', logical_pattern),
            ('KEYWORD', keyword_pattern),
            ('OPERATOR', r'==|!=|<=|>=|[+\-*/%=<>]'),
            ('DELIMITER', r'[(){}]'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('MISMATCH', r'.')
        ]

        # Собираем в одно большое выражение
        self.regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_patterns))

    def highlight(self):
        """Запускает отложенную подсветку синтаксиса"""
        if self.highlight_job:
            self.text_widget.after_cancel(self.highlight_job)
        self.highlight_job = self.text_widget.after(100, self.apply_highlight)

    def apply_highlight(self):
        """Применяет улучшенную подсветку синтаксиса ко всему тексту"""
        try:
            # Очищаем все теги
            tags_to_remove = ["keyword", "logical", "boolean", "string", "number", "comment", "operator", "delimiter"]
            for tag in tags_to_remove:
                self.text_widget.tag_remove(tag, "1.0", tk.END)

            content = self.text_widget.get("1.0", tk.END)

            for line_num, line in enumerate(content.splitlines(), 1):
                for match in self.regex.finditer(line):
                    kind = match.lastgroup
                    
                    # Применяем тег, если он определен
                    tag_name = kind.lower() if kind else None
                    if tag_name in tags_to_remove:
                        start = match.start()
                        end = match.end()
                        start_index = f"{line_num}.{start}"
                        end_index = f"{line_num}.{end}"
                        self.text_widget.tag_add(tag_name, start_index, end_index)

        except Exception as e:
            # Эта ошибка не должна прерывать работу IDE
            print(f"Ошибка подсветки синтаксиса: {e}")


class CodeEditor:
    """Улучшенный редактор кода с поддержкой автодополнения"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.current_file = None
        self.is_modified = False
        self.setup_editor()
    
    def setup_editor(self):
        """Настройка редактора"""
        try:
            # Создаем frame для редактора с номерами строк
            editor_frame = ttk.Frame(self.frame)
            editor_frame.pack(fill=tk.BOTH, expand=True)
            
            # Frame для номеров строк
            line_frame = tk.Frame(editor_frame, width=50, bg='#f0f0f0')
            line_frame.pack(side=tk.LEFT, fill=tk.Y)
            
            # Текстовое поле для номеров строк
            self.line_numbers = tk.Text(line_frame, width=4, padx=3, pady=3,
                                       bg='#f0f0f0', fg='#808080', state=tk.DISABLED,
                                       wrap=tk.NONE, font=("Consolas", 11))
            self.line_numbers.pack(fill=tk.BOTH, expand=True)
            
            # Основное текстовое поле
            self.text_area = scrolledtext.ScrolledText(
                editor_frame,
                wrap=tk.NONE,
                font=("Consolas", 11),
                undo=True,
                maxundo=50,
                selectbackground='#316AC5',
                insertbackground='black',
                bg='white',
                fg='black',
                insertwidth=2
            )
            self.text_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            
            # Настройка подсветки синтаксиса
            self.highlighter = SyntaxHighlighter(self.text_area)
            
            # Привязка событий
            self.text_area.bind('<KeyRelease>', self.on_key_release)
            self.text_area.bind('<Button-1>', self.on_click)
            self.text_area.bind('<MouseWheel>', self.on_mousewheel)
            self.text_area.bind('<<Modified>>', self.on_modified)
            self.text_area.bind('<Control-space>', self.show_autocomplete)
            
            # Синхронизация прокрутки
            self.text_area.config(yscrollcommand=self.sync_scroll)
            
            # Инициализация номеров строк
            self.update_line_numbers()
            
        except Exception as e:
            print(f"Ошибка настройки редактора: {e}")
            traceback.print_exc()
            raise
    
    def show_autocomplete(self, event=None):
        """Показывает автодополнение (простая версия)"""
        try:
            # Список ключевых слов для автодополнения
            keywords = ['say', 'kas', 'if', 'else', 'true', 'false', 'and', 'or', 'not']
            
            # Получаем текущее слово
            current_pos = self.text_area.index(tk.INSERT)
            line_start = current_pos.rsplit('.', 1)[0] + '.0'
            line_text = self.text_area.get(line_start, current_pos)
            
            # Находим последнее слово
            words = re.findall(r'\w+', line_text)
            if words:
                partial = words[-1]
                matches = [kw for kw in keywords if kw.startswith(partial)]
                
                if matches and len(matches) == 1 and matches[0] != partial:
                    # Автоматически дополняем если есть одно совпадение
                    completion = matches[0][len(partial):]
                    self.text_area.insert(tk.INSERT, completion)
                elif len(matches) > 1:
                    # Показываем список если несколько вариантов
                    messagebox.showinfo("Автодополнение", f"Возможные варианты: {', '.join(matches)}")
            
        except Exception as e:
            print(f"Ошибка автодополнения: {e}")
    
    def sync_scroll(self, *args):
        """Синхронизация прокрутки номеров строк и текста"""
        try:
            self.line_numbers.yview_moveto(args[0])
            if hasattr(self.text_area, 'vbar'):
                self.text_area.vbar.set(*args)
        except Exception as e:
            print(f"Ошибка синхронизации прокрутки: {e}")
    
    def on_key_release(self, event=None):
        """Обновление после нажатия клавиши"""
        try:
            self.update_line_numbers()
            self.highlighter.highlight()
            if hasattr(self.parent, 'update_status'):
                self.parent.update_status()
        except Exception as e:
            print(f"Ошибка обработки нажатия клавиши: {e}")
    
    def on_click(self, event=None):
        """Обновление после клика мыши"""
        try:
            self.update_line_numbers()
            if hasattr(self.parent, 'update_status'):
                self.parent.update_status()
        except Exception as e:
            print(f"Ошибка обработки клика: {e}")
    
    def on_mousewheel(self, event=None):
        """Синхронизация при прокрутке колесом"""
        try:
            # Прокручиваем основную область текста, а sync_scroll обновит номера строк
            self.text_area.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"
        except Exception as e:
            print(f"Ошибка прокрутки: {e}")
    
    def on_modified(self, event=None):
        """Обработчик изменения текста"""
        try:
            if not self.is_modified:
                self.is_modified = True
                if hasattr(self.parent, 'update_title'):
                    self.parent.update_title()
        except Exception as e:
            print(f"Ошибка обработки изменений: {e}")
    
    def update_line_numbers(self):
        """Обновление номеров строк"""
        try:
            self.line_numbers.config(state=tk.NORMAL)
            self.line_numbers.delete("1.0", tk.END)
            
            line_count = int(self.text_area.index(tk.END).split('.')[0]) - 1
            line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
            
            self.line_numbers.insert("1.0", line_numbers_string)
            self.line_numbers.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Ошибка обновления номеров строк: {e}")
    
    def get_text(self):
        """Получить весь текст"""
        try:
            return self.text_area.get("1.0", tk.END + "-1c")
        except Exception as e:
            print(f"Ошибка получения текста: {e}")
            return ""
    
    def set_text(self, text):
        """Установить текст"""
        try:
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", text)
            self.update_line_numbers()
            self.highlighter.highlight()
            self.is_modified = False
        except Exception as e:
            print(f"Ошибка установки текста: {e}")
    
    def insert_text(self, text):
        """Вставить текст в текущую позицию"""
        try:
            self.text_area.insert(tk.INSERT, text)
            self.update_line_numbers()
            self.highlighter.highlight()
        except Exception as e:
            print(f"Ошибка вставки текста: {e}")
    
    def get_cursor_position(self):
        """Получить позицию курсора"""
        try:
            return self.text_area.index(tk.INSERT)
        except Exception as e:
            print(f"Ошибка получения позиции курсора: {e}")
            return "1.0"


class Console:
    """Улучшенная консоль для вывода результатов"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.setup_console()
    
    def setup_console(self):
        """Настройка консоли"""
        try:
            # Заголовок консоли с дополнительной информацией
            header_frame = ttk.Frame(self.frame)
            header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
            
            console_label = ttk.Label(header_frame, text="🖥️ Console Output", font=("Arial", 10, "bold"))
            console_label.pack(side=tk.LEFT)
            
            # Кнопка очистки консоли
            clear_button = ttk.Button(header_frame, text="🧹 Clear", command=self.clear)
            clear_button.pack(side=tk.RIGHT)
            
            # Текстовое поле консоли с улучшенными цветами
            self.console_text = scrolledtext.ScrolledText(
                self.frame,
                height=12,
                wrap=tk.WORD,
                font=("Consolas", 10),
                bg='#1e1e1e',
                fg='#ffffff',
                insertbackground='white',
                state=tk.DISABLED
            )
            self.console_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Настройка тегов для цветного вывода
            self.console_text.tag_config("output", foreground="#00ff88")
            self.console_text.tag_config("error", foreground="#ff4444")
            self.console_text.tag_config("info", foreground="#4488ff")
            self.console_text.tag_config("warning", foreground="#ffaa00")
            self.console_text.tag_config("success", foreground="#88ff44")
            self.console_text.tag_config("boolean", foreground="#ff88ff")
            self.console_text.tag_config("number", foreground="#88aaff")
            
        except Exception as e:
            print(f"Ошибка настройки консоли: {e}")
            traceback.print_exc()
            raise
    
    def write(self, text, tag="output"):
        """Запись текста в консоль с улучшенным форматированием"""
        try:
            self.console_text.config(state=tk.NORMAL)
            
            # Автоматическое определение типа вывода
            if "true" in text.lower() or "false" in text.lower():
                if tag == "output":  # Только если не указан специальный тег
                    tag = "boolean"
            elif re.search(r'\d+', text):
                if tag == "output" and not any(char.isalpha() for char in text if char not in "0123456789. "):
                    tag = "number"
            
            self.console_text.insert(tk.END, text, tag)
            self.console_text.see(tk.END)
            self.console_text.config(state=tk.DISABLED)
            self.console_text.update()
        except Exception as e:
            print(f"Ошибка записи в консоль: {e}")
    
    def clear(self):
        """Очистка консоли"""
        try:
            self.console_text.config(state=tk.NORMAL)
            self.console_text.delete("1.0", tk.END)
            self.console_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Ошибка очистки консоли: {e}")
    
    def write_info(self, text):
        """Информационное сообщение"""
        self.write(f"ℹ️ {text}\n", "info")
    
    def write_error(self, text):
        """Сообщение об ошибке"""
        self.write(f"❌ {text}\n", "error")
    
    def write_warning(self, text):
        """Предупреждение"""
        self.write(f"⚠️ {text}\n", "warning")
    
    def write_success(self, text):
        """Успешное выполнение"""
        self.write(f"✅ {text}\n", "success")


class TemplateManager:
    """Менеджер шаблонов кода"""
    
    @staticmethod
    def get_templates():
        """Возвращает словарь доступных шаблонов"""
        return {
            "Hello World": '''# Hello World на DoroLang
say "Hello, DoroLang!"
say "Добро пожаловать в мир программирования!"''',
            
            "Variables": '''# Работа с переменными
kas name = "Ваше имя"
kas age = 25
kas is_student = true

say "Имя: " + name
say "Возраст: " + age
say "Студент: " + is_student''',
            
            "Conditional Logic": '''# Условная логика
kas score = 85
kas passed = score >= 60

if (passed) {
    say "Поздравляем! Вы прошли тест!"
    kas grade = "Зачёт"
} else {
    say "К сожалению, тест не пройден"
    kas grade = "Незачёт"
}

say "Итоговая оценка: " + grade''',
            
            "Complex Logic": '''# Сложная логика
kas temperature = 22
kas is_sunny = true
kas is_weekend = false

kas good_weather = temperature > 20 and is_sunny
kas can_go_out = good_weather and (is_weekend or temperature > 25)

if (can_go_out) {
    say "Отличная погода для прогулки!"
} else {
    if (not good_weather) {
        say "Погода не очень хорошая"
    } else {
        say "Погода хорошая, но сегодня рабочий день"
    }
}''',
            
            "Calculator": '''# Простой калькулятор
kas a = 15
kas b = 7

say "Число A: " + a
say "Число B: " + b
say "Сумма: " + (a + b)
say "Разность: " + (a - b)
say "Произведение: " + (a * b)
say "Частное: " + (a / b)
say "Остаток: " + (a % b)

# Сравнения
say "A больше B: " + (a > b)
say "A равно B: " + (a == b)
say "A не равно B: " + (a != b)'''
        }


class DoroLangIDE(tk.Tk):
    """Главный класс улучшенной IDE для DoroLang"""
    
    def __init__(self):
        super().__init__()
        try:
            print("Инициализация Enhanced DoroLang IDE...")

            self.title("DoroLang IDE v1.1 - Enhanced Edition")
            self.geometry("1400x900")
            self.minsize(900, 700)
            
            # Проверяем доступность модулей DoroLang
            if DOROLANG_MODULES_OK and Interpreter:
                self.dorolang_interpreter = Interpreter()
                print("✅ Используется настоящий интерпретатор DoroLang")
            else:
                self.dorolang_interpreter = MockInterpreter()
                print("⚠️ Используется демо-режим (модули DoroLang не загружены)")
            
            # Настройка стиля
            self.setup_style()
            
            # Создание компонентов
            print("Создание интерфейса...")
            self.setup_menu()
            self.setup_toolbar()
            self.setup_main_area()
            self.setup_statusbar()
            
            # Настройки
            self.recent_files = []
            self.load_settings()
            
            # Привязка событий
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.bind_shortcuts()
            
            # Создаем новый файл по умолчанию с шаблоном
            self.new_file_with_template()
            
            # Приветственное сообщение
            if DOROLANG_MODULES_OK:
                self.console.write_info("Enhanced DoroLang IDE v1.1 запущена!")
                self.console.write_info("Новые возможности: булевы значения, логические операторы, условия")
                self.console.write_info("Нажмите F5 для запуска кода, Ctrl+Space для автодополнения")
            else:
                self.console.write_warning("IDE запущена в демо-режиме.")
                self.console.write_warning("Для полной функциональности поместите lexer.py, parser.py, interpreter.py в ту же папку.")
            
            print("✅ Enhanced DoroLang IDE успешно инициализирована!")
            
        except Exception as e:
            print(f"❌ Критическая ошибка инициализации: {e}")
            traceback.print_exc()
            raise
    
    def bind_shortcuts(self):
        """Привязка расширенных горячих клавиш"""
        try:
            self.bind('<Control-n>', lambda e: self.new_file())
            self.bind('<Control-o>', lambda e: self.open_file())
            self.bind('<Control-s>', lambda e: self.save_file())
            self.bind('<Control-Shift-S>', lambda e: self.save_as_file())
            self.bind('<F5>', lambda e: self.run_code())
            self.bind('<F9>', lambda e: self.run_selection())
            self.bind('<Control-t>', lambda e: self.show_template_dialog())
            self.bind('<Control-slash>', lambda e: self.toggle_comment())
        except Exception as e:
            print(f"Ошибка привязки горячих клавиш: {e}")
    
    def setup_style(self):
        """Улучшенная настройка стилей"""
        try:
            style = ttk.Style()
            # Используем доступную тему
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif available_themes:
                style.theme_use(available_themes[0])
                
            # Настраиваем цвета
            style.configure('Toolbar.TFrame', background='#f0f0f0')
        except Exception as e:
            print(f"Ошибка настройки стилей: {e}")
    
    def setup_menu(self):
        """Создание расширенного меню"""
        try:
            menubar = tk.Menu(self)
            self.config(menu=menubar)
            
            # Файл
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="📁 Файл", menu=file_menu)
            file_menu.add_command(label="Новый файл (Ctrl+N)", command=self.new_file)
            file_menu.add_command(label="Из шаблона (Ctrl+T)", command=self.show_template_dialog)
            file_menu.add_separator()
            file_menu.add_command(label="Открыть файл (Ctrl+O)", command=self.open_file)
            file_menu.add_separator()
            file_menu.add_command(label="Сохранить (Ctrl+S)", command=self.save_file)
            file_menu.add_command(label="Сохранить как (Ctrl+Shift+S)", command=self.save_as_file)
            file_menu.add_separator()
            file_menu.add_command(label="Выход", command=self.on_closing)
            
            # Правка
            edit_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="✏️ Правка", menu=edit_menu)
            edit_menu.add_command(label="Отменить (Ctrl+Z)", command=self.undo)
            edit_menu.add_command(label="Повторить (Ctrl+Y)", command=self.redo)
            edit_menu.add_separator()
            edit_menu.add_command(label="Вырезать (Ctrl+X)", command=self.cut)
            edit_menu.add_command(label="Копировать (Ctrl+C)", command=self.copy)
            edit_menu.add_command(label="Вставить (Ctrl+V)", command=self.paste)
            edit_menu.add_command(label="Выделить все (Ctrl+A)", command=self.select_all)
            edit_menu.add_separator()
            edit_menu.add_command(label="Комментировать (Ctrl+/)", command=self.toggle_comment)
            edit_menu.add_command(label="Автодополнение (Ctrl+Space)", command=self.editor.show_autocomplete)
            
            # Запуск
            run_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="▶️ Запуск", menu=run_menu)
            run_menu.add_command(label="Запустить код (F5)", command=self.run_code)
            run_menu.add_command(label="Запустить выделенное (F9)", command=self.run_selection)
            run_menu.add_separator()
            run_menu.add_command(label="Очистить консоль", command=self.clear_console)
            run_menu.add_command(label="Сбросить переменные", command=self.reset_interpreter)
            
            # Инструменты
            tools_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="🔧 Инструменты", menu=tools_menu)
            tools_menu.add_command(label="Шаблоны кода", command=self.show_template_dialog)
            tools_menu.add_command(label="Проверить синтаксис", command=self.check_syntax)
            tools_menu.add_separator()
            tools_menu.add_command(label="Настройки", command=self.show_settings)
            
            # Справка
            help_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="❓ Справка", menu=help_menu)
            help_menu.add_command(label="Синтаксис DoroLang", command=self.show_syntax_help)
            help_menu.add_command(label="Горячие клавиши", command=self.show_shortcuts)
            help_menu.add_separator()
            help_menu.add_command(label="О программе", command=self.show_about)
            
        except Exception as e:
            print(f"Ошибка создания меню: {e}")
    
    def setup_toolbar(self):
        """Создание улучшенной панели инструментов"""
        try:
            toolbar = ttk.Frame(self, style='Toolbar.TFrame')
            toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
            
            # Кнопки файлов
            ttk.Button(toolbar, text="📄 Новый", command=self.new_file).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="📋 Шаблон", command=self.show_template_dialog).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="📁 Открыть", command=self.open_file).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="💾 Сохранить", command=self.save_file).pack(side=tk.LEFT, padx=2)
            
            ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
            # Кнопки запуска
            ttk.Button(toolbar, text="▶️ Запустить (F5)", command=self.run_code).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="🔄 Выделенное (F9)", command=self.run_selection).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="🧹 Очистить", command=self.clear_console).pack(side=tk.LEFT, padx=2)
            
            ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
            # Кнопки инструментов
            ttk.Button(toolbar, text="✔️ Синтаксис", command=self.check_syntax).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="💬 Комментарий", command=self.toggle_comment).pack(side=tk.LEFT, padx=2)
            
            ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
            # Информация
            self.line_col_label = ttk.Label(toolbar, text="Строка: 1, Столбец: 1")
            self.line_col_label.pack(side=tk.RIGHT, padx=5)
            
            # Индикатор режима
            mode_text = "Full Mode" if DOROLANG_MODULES_OK else "Demo Mode"
            self.mode_label = ttk.Label(toolbar, text=f"[{mode_text}]", font=("Arial", 8))
            self.mode_label.pack(side=tk.RIGHT, padx=10)
            
        except Exception as e:
            print(f"Ошибка создания панели инструментов: {e}")
    
    def setup_main_area(self):
        """Создание основной рабочей области"""
        try:
            # Создаем PanedWindow для разделения редактора и консоли
            self.paned_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
            self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Редактор кода
            self.editor = CodeEditor(self)
            self.paned_window.add(self.editor.frame, weight=3)
            
            # Консоль
            self.console = Console(self)
            self.paned_window.add(self.console.frame, weight=1)
            
        except Exception as e:
            print(f"Ошибка создания основной области: {e}")
            traceback.print_exc()
            raise
    
    def setup_statusbar(self):
        """Создание строки состояния"""
        try:
            self.statusbar = ttk.Frame(self)
            self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            self.status_label = ttk.Label(self.statusbar, text="Готов к работе")
            self.status_label.pack(side=tk.LEFT, padx=5)
            
            # Индикатор изменений
            self.modified_label = ttk.Label(self.statusbar, text="")
            self.modified_label.pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            print(f"Ошибка создания строки состояния: {e}")
    
    def new_file_with_template(self):
        """Создание нового файла с базовым шаблоном"""
        try:
            welcome_template = '''# Добро пожаловать в DoroLang v1.1!
# Новые возможности: булевы значения, логика, условия

say "Привет, DoroLang!"

# Попробуйте новые возможности:
kas name = "Программист"
kas is_learning = true

if (is_learning) {
    say name + " изучает DoroLang!"
} else {
    say name + " уже знает DoroLang"
}
'''
            self.editor.set_text(welcome_template)
            self.editor.current_file = None
            self.editor.is_modified = False
            self.update_title()
        except Exception as e:
            print(f"Ошибка создания шаблона: {e}")
    
    def show_template_dialog(self):
        """Показывает диалог выбора шаблона"""
        try:
            templates = TemplateManager.get_templates()
            
            # Создаем диалоговое окно
            dialog = tk.Toplevel(self)
            dialog.title("Выбор шаблона кода")
            dialog.geometry("400x300")
            dialog.transient(self)
            dialog.grab_set()
            
            # Список шаблонов
            listbox = tk.Listbox(dialog, font=("Arial", 10))
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for template_name in templates.keys():
                listbox.insert(tk.END, template_name)
            
            # Кнопки
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            def apply_template():
                selection = listbox.curselection()
                if selection:
                    template_name = listbox.get(selection[0])
                    self.editor.set_text(templates[template_name])
                    self.editor.current_file = None
                    self.editor.is_modified = True
                    self.update_title()
                    dialog.destroy()
            
            ttk.Button(button_frame, text="Применить", command=apply_template).pack(side=tk.LEFT)
            ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.RIGHT)
            
            # Автовыбор первого элемента
            if templates:
                listbox.selection_set(0)
                listbox.bind('<Double-Button-1>', lambda e: apply_template())
            
        except Exception as e:
            print(f"Ошибка диалога шаблонов: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть диалог шаблонов: {e}")
    
    def toggle_comment(self):
        """Переключает комментарий для выделенных строк"""
        try:
            # Получаем выделенный текст или текущую строку
            try:
                start_idx = self.editor.text_area.index(tk.SEL_FIRST)
                end_idx = self.editor.text_area.index(tk.SEL_LAST)
            except tk.TclError:
                # Если нет выделения, работаем с текущей строкой
                current_line = self.editor.text_area.index(tk.INSERT).split('.')[0]
                start_idx = f"{current_line}.0"
                end_idx = f"{current_line}.end"
            
            # Получаем текст
            text = self.editor.text_area.get(start_idx, end_idx)
            lines = text.split('\n')
            
            # Проверяем, нужно ли добавить или удалить комментарии
            all_commented = all(line.strip().startswith('#') or line.strip() == '' for line in lines)
            
            # Обрабатываем каждую строку
            new_lines = []
            for line in lines:
                if all_commented:
                    # Удаляем комментарий
                    if line.strip().startswith('#'):
                        # Убираем первый # и один пробел после него если есть
                        new_line = line.replace('#', '', 1)
                        if new_line.startswith(' '):
                            new_line = new_line[1:]
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)
                else:
                    # Добавляем комментарий
                    if line.strip():  # Не комментируем пустые строки
                        new_lines.append('# ' + line)
                    else:
                        new_lines.append(line)
            
            # Заменяем текст
            self.editor.text_area.delete(start_idx, end_idx)
            self.editor.text_area.insert(start_idx, '\n'.join(new_lines))
            
        except Exception as e:
            print(f"Ошибка переключения комментария: {e}")
    
    def check_syntax(self):
        """Проверяет синтаксис без выполнения"""
        try:
            if not DOROLANG_MODULES_OK:
                self.console.write_warning("Проверка синтаксиса недоступна в демо-режиме")
                return
            
            code = self.editor.get_text().strip()
            if not code:
                self.console.write_warning("Нет кода для проверки!")
                return
            
            self.console.write_info("Проверка синтаксиса...")
            
            try:
                # Только лексер и парсер
                lexer = Lexer(code)
                tokens = lexer.tokenize()
                
                parser = Parser(tokens)
                ast = parser.parse()
                
                self.console.write_success(f"Синтаксис корректен! Найдено {len(ast.statements)} утверждений")
                
            except LexerError as e:
                self.console.write_error(f"Ошибка лексера: {e}")
            except ParseError as e:
                self.console.write_error(f"Синтаксическая ошибка: {e}")
            except Exception as e:
                self.console.write_error(f"Неожиданная ошибка: {e}")
                
        except Exception as e:
            print(f"Ошибка проверки синтаксиса: {e}")
            self.console.write_error(f"Ошибка проверки: {e}")
    
    def show_syntax_help(self):
        """Показывает справку по синтаксису DoroLang"""
        help_text = """DoroLang v1.1 - Справка по синтаксису

ОСНОВНЫЕ КОНСТРУКЦИИ:
• say "текст"              - вывод текста
• kas переменная = значение - объявление переменной

ТИПЫ ДАННЫХ:
• Числа: 42, 3.14
• Строки: "привет", 'мир'
• Булевы: true, false

ОПЕРАТОРЫ:
• Арифметические: +, -, *, /, %
• Сравнения: ==, !=, <, >, <=, >=
• Логические: and, or, not

УСЛОВНЫЕ КОНСТРУКЦИИ:
if (условие) {
    # код если истина
} else {
    # код если ложь
}

КОММЕНТАРИИ:
# Это комментарий

ПРИМЕРЫ:
kas age = 25
if (age >= 18) {
    say "Совершеннолетний"
} else {
    say "Несовершеннолетний"
}

kas result = (age > 20) and (age < 30)
say "Возраст от 20 до 30: " + result
"""
        messagebox.showinfo("Синтаксис DoroLang", help_text)
    
    def show_shortcuts(self):
        """Показывает горячие клавиши"""
        shortcuts_text = """Горячие клавиши DoroLang IDE

ФАЙЛЫ:
Ctrl+N        - Новый файл
Ctrl+T        - Новый из шаблона
Ctrl+O        - Открыть файл
Ctrl+S        - Сохранить
Ctrl+Shift+S  - Сохранить как

РЕДАКТИРОВАНИЕ:
Ctrl+Z        - Отменить
Ctrl+Y        - Повторить
Ctrl+X        - Вырезать
Ctrl+C        - Копировать
Ctrl+V        - Вставить
Ctrl+A        - Выделить все
Ctrl+/        - Комментарий
Ctrl+Space    - Автодополнение

ВЫПОЛНЕНИЕ:
F5            - Запустить код
F9            - Запустить выделенное
"""
        messagebox.showinfo("Горячие клавиши", shortcuts_text)
    
    def show_settings(self):
        """Показывает окно настроек (заглушка)"""
        messagebox.showinfo("Настройки", "Окно настроек будет добавлено в следующей версии")
    
    def update_status(self):
        """Обновление строки состояния"""
        try:
            cursor_pos = self.editor.get_cursor_position()
            line, col = cursor_pos.split('.')
            self.line_col_label.config(text=f"Строка: {line}, Столбец: {int(col) + 1}")
        except Exception as e:
            print(f"Ошибка обновления статуса: {e}")
    
    def update_title(self):
        """Обновление заголовка окна"""
        try:
            filename = self.editor.current_file if self.editor.current_file else "Без названия"
            modified_mark = " *" if self.editor.is_modified else ""
            mode_suffix = "" if DOROLANG_MODULES_OK else " (DEMO MODE)"
            self.title(f"DoroLang IDE v1.1 - {filename}{modified_mark}{mode_suffix}")
        except Exception as e:
            print(f"Ошибка обновления заголовка: {e}")
    
    # Методы для работы с файлами (аналогично предыдущей версии)
    def new_file(self):
        """Создание нового файла"""
        try:
            if self.check_save_changes():
                self.editor.set_text("")
                self.editor.current_file = None
                self.editor.is_modified = False
                self.update_title()
                self.status_label.config(text="Новый файл создан")
        except Exception as e:
            print(f"Ошибка создания нового файла: {e}")
            messagebox.showerror("Ошибка", f"Не удалось создать новый файл: {e}")
    
    def open_file(self):
        """Открытие файла"""
        try:
            if not self.check_save_changes():
                return
            
            filename = filedialog.askopenfilename(
                title="Открыть файл DoroLang",
                filetypes=[
                    ("DoroLang files", "*.doro"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.editor.set_text(content)
                self.editor.current_file = filename
                self.editor.is_modified = False
                self.update_title()
                self.status_label.config(text=f"Файл открыт: {os.path.basename(filename)}")
                
        except Exception as e:
            print(f"Ошибка открытия файла: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
    
    def save_file(self):
        """Сохранение файла"""
        try:
            if self.editor.current_file:
                with open(self.editor.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.get_text())
                
                self.editor.is_modified = False
                self.update_title()
                self.status_label.config(text=f"Файл сохранен: {os.path.basename(self.editor.current_file)}")
                return True
            else:
                return self.save_as_file()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
            return False
    
    def save_as_file(self):
        """Сохранение файла как..."""
        try:
            filename = filedialog.asksaveasfilename(
                title="Сохранить файл DoroLang",
                defaultextension=".doro",
                filetypes=[
                    ("DoroLang files", "*.doro"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.editor.get_text())
                
                self.editor.current_file = filename
                self.editor.is_modified = False
                self.update_title()
                self.status_label.config(text=f"Файл сохранен: {os.path.basename(filename)}")
                return True
            return False
        except Exception as e:
            print(f"Ошибка сохранения файла как: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
            return False
    
    def check_save_changes(self):
        """Проверка на несохраненные изменения"""
        try:
            if self.editor.is_modified:
                result = messagebox.askyesnocancel(
                    "Несохраненные изменения",
                    "Сохранить изменения в текущем файле?"
                )
                if result is True:
                    return self.save_file()
                elif result is False:
                    return True
                else:  # Cancel
                    return False
            return True
        except Exception as e:
            print(f"Ошибка проверки изменений: {e}")
            return True
    
    # Методы редактирования
    def undo(self):
        """Отмена"""
        try:
            self.editor.text_area.event_generate('<<Undo>>')
        except Exception as e:
            print(f"Ошибка отмены: {e}")
    
    def redo(self):
        """Повтор"""
        try:
            self.editor.text_area.event_generate('<<Redo>>')
        except Exception as e:
            print(f"Ошибка повтора: {e}")
    
    def cut(self):
        """Вырезать"""
        try:
            self.editor.text_area.event_generate('<<Cut>>')
        except Exception as e:
            print(f"Ошибка вырезания: {e}")
    
    def copy(self):
        """Копировать"""
        try:
            self.editor.text_area.event_generate('<<Copy>>')
        except Exception as e:
            print(f"Ошибка копирования: {e}")
    
    def paste(self):
        """Вставить"""
        try:
            self.editor.text_area.event_generate('<<Paste>>')
        except Exception as e:
            print(f"Ошибка вставки: {e}")
    
    def select_all(self):
        """Выделить все"""
        try:
            self.editor.text_area.event_generate('<<SelectAll>>')
        except Exception as e:
            print(f"Ошибка выделения всего: {e}")
    
    # Методы выполнения кода
    def run_code(self):
        """Запуск всего кода"""
        try:
            code = self.editor.get_text().strip()
            if not code:
                self.console.write_warning("Нет кода для выполнения!")
                return
            
            self.console.clear()
            self.console.write_info("Запуск программы...")
            
            # Запускаем в отдельном потоке чтобы не блокировать GUI
            thread = threading.Thread(target=self._execute_code, args=(code,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            print(f"Ошибка запуска кода: {e}")
            self.console.write_error(f"Ошибка запуска: {e}")
    
    def run_selection(self):
        """Запуск выделенного кода"""
        try:
            selected_text = self.editor.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text.strip():
                self.console.clear()
                self.console.write_info("Запуск выделенного кода...")
                
                thread = threading.Thread(target=self._execute_code, args=(selected_text,))
                thread.daemon = True
                thread.start()
            else:
                self.console.write_warning("Нет выделенного текста!")
        except tk.TclError:
            self.console.write_warning("Нет выделенного текста!")
        except Exception as e:
            print(f"Ошибка запуска выделения: {e}")
            self.console.write_error(f"Ошибка запуска выделения: {e}")
    
    def _execute_code(self, code):
        """Выполнение кода DoroLang"""
        try:
            if not DOROLANG_MODULES_OK:
                # Демо-режим
                output = self.dorolang_interpreter.interpret(code)
                for line in output:
                    self.console.write(line + "\n", "warning")
                return
            
            # Создаем экземпляры компонентов DoroLang
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Выполняем код
            output = self.dorolang_interpreter.interpret(ast)
            
            # Выводим результат
            if output:
                for line in output:
                    if "❌" in line:
                        self.console.write(line + "\n", "error")
                    else:
                        self.console.write(line + "\n", "output")
            
            # Показываем статистику
            variables = self.dorolang_interpreter.get_variables()
            if variables:
                self.console.write_info(f"Переменных в памяти: {len(variables)}")
            
            self.console.write_success("Выполнение завершено!")
            
        except Exception as e:
            if DOROLANG_MODULES_OK:
                if isinstance(e, LexerError):
                    self.console.write_error(f"Ошибка лексера: {e}")
                elif isinstance(e, ParseError):
                    self.console.write_error(f"Синтаксическая ошибка: {e}")
                elif isinstance(e, DoroRuntimeError):
                    self.console.write_error(f"Ошибка выполнения: {e}")
                else:
                    self.console.write_error(f"Неожиданная ошибка: {e}")
            else:
                self.console.write_error(f"Ошибка выполнения: {e}")
            
            print(f"Ошибка выполнения кода: {e}")
            traceback.print_exc()
    
    def clear_console(self):
        """Очистка консоли"""
        try:
            self.console.clear()
            self.console.write_info("Консоль очищена")
        except Exception as e:
            print(f"Ошибка очистки консоли: {e}")
    
    def reset_interpreter(self):
        """Сброс интерпретатора"""
        try:
            self.dorolang_interpreter.reset()
            self.console.write_info("Переменные интерпретатора сброшены")
        except Exception as e:
            print(f"Ошибка сброса интерпретатора: {e}")
            self.console.write_error(f"Ошибка сброса: {e}")
    
    def load_settings(self):
        """Загрузка настроек"""
        try:
            settings_file = "dorolang_ide_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.recent_files = settings.get('recent_files', [])
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            self.recent_files = []
    
    def save_settings(self):
        """Сохранение настроек"""
        try:
            settings_file = "dorolang_ide_settings.json"
            settings = {
                'recent_files': self.recent_files
            }
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def show_about(self):
        """О программе"""
        try:
            mode_info = "Полный режим" if DOROLANG_MODULES_OK else "Демо-режим"
            about_text = f"""DoroLang IDE v1.1 - Enhanced Edition
Режим: {mode_info}

Интегрированная среда разработки 
для языка программирования DoroLang

Автор: Dorofii Karnaukh
Год: 2024

Новые возможности v1.1:
✨ Булевы значения (true/false)
✨ Логические операторы (and/or/not)
✨ Условные конструкции (if/else)
✨ Улучшенная подсветка синтаксиса
✨ Автодополнение кода
✨ Шаблоны кода
✨ Проверка синтаксиса
✨ Комментирование строк

Базовые возможности:
✅ Редактор с подсветкой синтаксиса
✅ Номера строк
✅ Интерактивная консоль
✅ Горячие клавиши
✅ Работа с файлами

DoroLang - простой и мощный язык 
программирования для обучения!"""
            
            messagebox.showinfo("О программе", about_text)
        except Exception as e:
            print(f"Ошибка показа о программе: {e}")
    
    def on_closing(self):
        """Обработчик закрытия приложения"""
        try:
            if self.check_save_changes():
                self.save_settings()
                self.destroy()
        except Exception as e:
            print(f"Ошибка закрытия приложения: {e}")
            self.destroy()  # Принудительно закрываем
    
    def run(self):
        """Запуск IDE"""
        try:
            print("Запуск главного цикла приложения...")
            self.mainloop()
        except Exception as e:
            print(f"Ошибка главного цикла: {e}")
            traceback.print_exc()


def main():
    """Главная функция запуска Enhanced DoroLang IDE"""
    
    print("=" * 60)
    print("🚀 ЗАПУСК ENHANCED DOROLANG IDE v1.1")
    print("=" * 60)
    
    try:
        # Диагностика системы
        print(f"Python версия: {sys.version}")
        print(f"Рабочая папка: {os.getcwd()}")
        print(f"Файлы в папке: {os.listdir('.')}")
        
        # Проверка tkinter
        try:
            import tkinter
            print("✅ Tkinter доступен")
        except ImportError as e:
            print(f"❌ Tkinter недоступен: {e}")
            return
        
        # Создаем и запускаем IDE
        print("\nСоздание экземпляра Enhanced IDE...")
        ide = DoroLangIDE()
        
        print("Enhanced IDE создана успешно, запуск...")
        ide.run()
        
        print("Enhanced IDE завершена.")
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("\nПолная трассировка ошибки:")
        traceback.print_exc()
        
        # Показываем окно с ошибкой если возможно
        try:
            import tkinter.messagebox as mb
            error_details = f"""Критическая ошибка запуска Enhanced IDE:

Ошибка: {str(e)}

Детали:
- Python: {sys.version}
- Рабочая папка: {os.getcwd()}
- Модули DoroLang: {'✅ OK' if DOROLANG_MODULES_OK else '❌ Не загружены'}

Проверьте:
1. Все ли нужные файлы в папке?
2. Установлены ли все зависимости?
3. Консольный вывод для деталей

Полная трассировка выведена в консоль."""
            
            mb.showerror("Критическая ошибка Enhanced DoroLang IDE", error_details)
        except:
            pass  # Если даже messagebox не работает
        
        print(f"\n💡 Возможные решения:")
        print("1. Убедитесь что файлы lexer.py, parser.py, interpreter.py в той же папке")
        print("2. Проверьте права доступа к файлам")  
        print("3. Попробуйте запустить из командной строки: python dorolang_ide.py")
        print("4. Проверьте версию Python (требуется 3.6+)")
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    if exit_code:
        sys.exit(exit_code)
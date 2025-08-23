#!/usr/bin/env python3
"""
DoroLang IDE - Главный модуль

Автор: Dorofii Karnaukh
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font, simpledialog
import shutil
import tkinter.scrolledtext as scrolledtext
import os
import sys
import threading
import io
import re
import json
import traceback

from ide_settings import THEMES
from ide_utils import (
    MockInterpreter,
    Lexer, LexerError, Parser, ParseError, Interpreter, DoroRuntimeError,
    DOROLANG_MODULES_OK
)
from ide_components import (
    CodeEditor,
    Console,
    FileExplorer,
    TemplateManager,
    FindReplaceDialog
)

class DoroLangIDE(tk.Tk):
    """Главный класс улучшенной IDE для DoroLang"""
    
    def __init__(self):
        super().__init__()
        try:
            print("Инициализация Enhanced DoroLang IDE...")

            self.title("DoroLang IDE")
            self.geometry("1400x900")
            self.minsize(900, 700)
            
            # Проверяем доступность модулей DoroLang
            # Иконки для закрытия вкладок
            # Серая иконка 'x' для обычного состояния
            self.img_close = tk.PhotoImage("img_close", data='''R0lGODlhCAAIAPABAJmZmf///yH5BAEAAAEALAAAAAAIAAgAAAIMBIKpqgYhADs=''')
            # Красная иконка 'x' для активного состояния (наведение/нажатие)
            self.img_close_active = tk.PhotoImage("img_close_active", data='''R0lGODlhCAAIAPABAO3t7f///yH5BAEAAAEALAAAAAAIAAgAAAIMBIKpqgYhADs=''')

            # Иконка для файлов .doro
            self.doro_icon = tk.PhotoImage("doro_icon", data='''
                R0lGODlhEAAQAPIAAAAAAP//AP8AAP/9/f//mf//Zv//M///AP/M/wAAAAAAACH5BAEAAAcALAAAAAAQABAAAANKeLrc/jDKSau9OOvNu/9gKI5kaZ5oqq5s675wLM90bd94ru987//AoHBILBqPyKRyyWw6n9CodEqtWq/YrHbL7Xq/4LB4TC6bz+i0es1uu9/wuHxOr9vv+Lx+z+/7/4CBgoOEhYaHiImKi4yNjo+AgZIAAAA7
            ''')
            if DOROLANG_MODULES_OK and Interpreter:
                self.dorolang_interpreter = Interpreter()
                print("✅ Используется настоящий интерпретатор DoroLang")
            else:
                self.dorolang_interpreter = MockInterpreter()
                print("⚠️ Используется демо-режим (модули DoroLang не загружены)")
            
            # Настройки
            self.current_theme = 'light' # Тема по умолчанию
            self.last_opened_folder = None
            self.notebook = None
            self.find_window = None
            self.editors = {}
            self.recent_files = []
            self.load_settings()
            self.theme_var = tk.StringVar(value=self.current_theme)
            
            # Настройка стиля
            self.setup_style()
            
            # Создание компонентов
            print("Создание интерфейса...")
            self.setup_main_area()
            self.setup_menu()
            self.setup_toolbar()
            self.setup_statusbar()
            
            # Применяем загруженную или стандартную тему
            self.apply_theme()
            
            # Загружаем последнюю открытую папку
            if self.last_opened_folder and os.path.isdir(self.last_opened_folder):
                self.file_explorer.populate_tree(self.last_opened_folder)
            
            # Привязка событий
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.bind_shortcuts()
            
            # Создаем новый файл по умолчанию с шаблоном
            self._create_new_tab(is_template=True)
            
            # Приветственное сообщение
            if DOROLANG_MODULES_OK:
                self.console.write_info("Enhanced DoroLang IDE запущена!")
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
            self.bind('<Control-f>', lambda e: self.show_find_dialog(False))
            self.bind('<Control-h>', lambda e: self.show_find_dialog(True))
            self.bind('<Control-g>', lambda e: self.go_to_line())
        except Exception as e:
            print(f"Ошибка привязки горячих клавиш: {e}")
    
    def setup_style(self):
        """Улучшенная настройка стилей"""
        try:
            style = ttk.Style()
            # Используем доступную тему, которая хорошо поддается настройке
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif 'alt' in available_themes:
                style.theme_use('alt')
            elif available_themes:
                style.theme_use(available_themes[0])

            style.element_create("close", "image", self.img_close,
                ("active", "pressed", "!disabled", self.img_close_active),
                ("active", "!disabled", self.img_close_active),
                border=8, sticky='e')

            style.layout("TNotebook.Tab", [
                ("Notebook.tab", {
                    "sticky": "nswe",
                    "children": [
                        ("Notebook.padding", {
                            "side": "top", "sticky": "nswe",
                            "children": [
                                ("Notebook.focus", {
                                    "side": "top", "sticky": "nswe",
                                    "children": [
                                        ("Notebook.label", {"side": "left", "sticky": ''}),
                                        ("close", {"side": "left", "sticky": ''}),
                                    ]
                                })
                            ]
                        })
                    ]
                })
            ])
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
            file_menu.add_command(label="Открыть папку...", command=self.open_folder)
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
            edit_menu.add_command(label="Найти... (Ctrl+F)", command=lambda: self.show_find_dialog(False))
            edit_menu.add_command(label="Заменить... (Ctrl+H)", command=lambda: self.show_find_dialog(True))
            edit_menu.add_command(label="Перейти к строке... (Ctrl+G)", command=self.go_to_line)
            edit_menu.add_separator()
            edit_menu.add_command(label="Комментировать (Ctrl+/)", command=self.toggle_comment)
            edit_menu.add_command(label="Автодополнение (Ctrl+Space)", command=self.show_autocomplete)
            
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
            
            # Вид
            view_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="🎨 Вид", menu=view_menu)

            theme_menu = tk.Menu(view_menu, tearoff=0)
            view_menu.add_cascade(label="Темы", menu=theme_menu)
            theme_menu.add_radiobutton(label="Светлая", variable=self.theme_var, value="light", command=self.switch_theme)
            theme_menu.add_radiobutton(label="Темная", variable=self.theme_var, value="dark", command=self.switch_theme)
            
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
            self.toolbar = ttk.Frame(self, style='Toolbar.TFrame')
            toolbar = self.toolbar
            self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
            
            # Кнопки файлов
            ttk.Button(toolbar, text="📄 Новый", command=self.new_file, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="📋 Шаблон", command=self.show_template_dialog, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="📁 Открыть", command=self.open_file, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="💾 Сохранить", command=self.save_file, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            
            ttk.Separator(toolbar, orient=tk.VERTICAL, style='Toolbar.TSeparator').pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
            # Кнопки запуска
            ttk.Button(toolbar, text="▶️ Запустить (F5)", command=self.run_code, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="🔄 Выделенное (F9)", command=self.run_selection, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="🧹 Очистить", command=self.clear_console, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            
            ttk.Separator(toolbar, orient=tk.VERTICAL, style='Toolbar.TSeparator').pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
            # Кнопки инструментов
            ttk.Button(toolbar, text="✔️ Синтаксис", command=self.check_syntax, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="💬 Комментарий", command=self.toggle_comment, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            
            ttk.Separator(toolbar, orient=tk.VERTICAL, style='Toolbar.TSeparator').pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
            # Информация
            self.line_col_label = ttk.Label(toolbar, text="Строка: 1, Столбец: 1", style='Toolbar.TLabel')
            self.line_col_label.pack(side=tk.RIGHT, padx=5)
            
            # Индикатор режима
            mode_text = "Full Mode" if DOROLANG_MODULES_OK else "Demo Mode"
            self.mode_label = ttk.Label(toolbar, text=f"[{mode_text}]", font=("Arial", 8), style='Toolbar.TLabel')
            self.mode_label.pack(side=tk.RIGHT, padx=10)
            
        except Exception as e:
            print(f"Ошибка создания панели инструментов: {e}")
    
    def setup_main_area(self):
        """Создание основной рабочей области"""
        try:
            # Главный горизонтальный разделитель
            main_paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
            main_paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 1. Проводник файлов (слева)
            self.file_explorer = FileExplorer(main_paned_window, self, doro_icon=self.doro_icon)
            main_paned_window.add(self.file_explorer.frame, weight=1)

            # 2. Правая панель (редактор + консоль)
            right_pane = ttk.Frame(main_paned_window)
            main_paned_window.add(right_pane, weight=4)

            # Вертикальный разделитель для редактора и консоли
            editor_console_pane = ttk.PanedWindow(right_pane, orient=tk.VERTICAL)
            editor_console_pane.pack(fill=tk.BOTH, expand=True)
            
            # Вкладки для редакторов
            self.notebook = ttk.Notebook(editor_console_pane, style='TNotebook')
            self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
            self.notebook.bind("<ButtonPress-1>", self.on_tab_close_press)
            editor_console_pane.add(self.notebook, weight=3)
            
            # Консоль
            self.console = Console(self)
            editor_console_pane.add(self.console.frame, weight=1)
        except Exception as e:
            print(f"Ошибка создания основной области: {e}")
            traceback.print_exc()
            raise
    
    def setup_statusbar(self):
        """Создание строки состояния"""
        try:
            self.statusbar = ttk.Frame(self, style='Statusbar.TFrame')
            self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            self.status_label = ttk.Label(self.statusbar, text="Готов к работе", style='Statusbar.TLabel')
            self.status_label.pack(side=tk.LEFT, padx=5)
            
            # Индикатор изменений
            self.modified_label = ttk.Label(self.statusbar, text="", style='Statusbar.TLabel')
            self.modified_label.pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            print(f"Ошибка создания строки состояния: {e}")
    
    def apply_welcome_template(self, editor):
        """Применяет приветственный шаблон к редактору"""
        welcome_template = '''# Добро пожаловать в DoroLang!
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
        editor.set_text(welcome_template)
    
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
                    editor = self.get_current_editor()
                    if editor:
                        editor.set_text(templates[template_name])
                        editor.is_modified = True
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
            editor = self.get_current_editor()
            if not editor: return

            # Получаем выделенный текст или текущую строку
            try:
                start_idx = editor.text_area.index(tk.SEL_FIRST)
                end_idx = editor.text_area.index(tk.SEL_LAST)
            except tk.TclError:
                # Если нет выделения, работаем с текущей строкой
                current_line = editor.text_area.index(tk.INSERT).split('.')[0]
                start_idx = f"{current_line}.0"
                end_idx = f"{current_line}.end"
            
            # Получаем текст
            text = editor.text_area.get(start_idx, end_idx)
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
            editor.text_area.delete(start_idx, end_idx)
            editor.text_area.insert(start_idx, '\n'.join(new_lines))
            
        except Exception as e:
            print(f"Ошибка переключения комментария: {e}")
    
    def check_syntax(self):
        """Проверяет синтаксис без выполнения"""
        try:
            if not DOROLANG_MODULES_OK:
                self.console.write_warning("Проверка синтаксиса недоступна в демо-режиме")
                return
            
            editor = self.get_current_editor()
            if not editor: return

            code = editor.get_text().strip()
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
        help_text = """DoroLang v1.2 - Справка по синтаксису

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
            editor = self.get_current_editor()
            if editor:
                cursor_pos = editor.get_cursor_position()
                line, col = cursor_pos.split('.')
                self.line_col_label.config(text=f"Строка: {line}, Столбец: {int(col) + 1}")
            else:
                self.line_col_label.config(text="")
        except Exception as e:
            print(f"Ошибка обновления статуса: {e}")
    
    def update_title(self):
        """Обновление заголовка окна"""
        try:
            editor = self.get_current_editor()
            if editor:
                filename = os.path.basename(editor.current_file) if editor.current_file else "Без названия"
                modified_mark = " *" if editor.is_modified else ""
                # Обновляем текст вкладки
                tab_id = self.notebook.select()
                self.notebook.tab(tab_id, text=f"{filename}{modified_mark} ") # Пробел для отступа от крестика
            else:
                filename = "Нет открытых файлов"
                modified_mark = ""

            theme_name = self.current_theme.capitalize()
            self.title(f"DoroLang IDE ({theme_name}) - {filename}{modified_mark}")
        except Exception as e:
            print(f"Ошибка обновления заголовка: {e}")
    
    # Методы для работы с файлами (аналогично предыдущей версии)
    def new_file(self):
        """Создание нового файла"""
        try:
            self._create_new_tab()
            self.status_label.config(text="Новый файл создан")
        except Exception as e:
            print(f"Ошибка создания нового файла: {e}")
            messagebox.showerror("Ошибка", f"Не удалось создать новый файл: {e}")

    def open_folder(self):
        """Открытие папки в проводнике"""
        try:
            path = filedialog.askdirectory(title="Выберите папку проекта")
            if path:
                self.file_explorer.populate_tree(path)
                self.last_opened_folder = path
                self.status_label.config(text=f"Папка открыта: {os.path.basename(path)}")
        except Exception as e:
            print(f"Ошибка открытия папки: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть папку: {e}")

    def open_file_from_path(self, path):
        """Открытие файла по указанному пути (для проводника)"""
        try:
            # Проверяем, не открыт ли файл уже
            for tab_id, editor in self.editors.items():
                if editor.current_file == path:
                    self.notebook.select(tab_id)
                    return
            
            # Если не открыт, создаем новую вкладку
            self._create_new_tab(file_path=path)
            self.status_label.config(text=f"Файл открыт: {os.path.basename(path)}")
        except Exception as e:
            print(f"Ошибка открытия файла по пути: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
    
    def open_file(self):
        """Открытие файла"""
        try:
            filename = filedialog.askopenfilename(
                title="Открыть файл DoroLang",
                filetypes=[
                    ("DoroLang files", "*.doro"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                self.open_file_from_path(filename)
        except Exception as e:
            print(f"Ошибка открытия файла: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    
    def save_file(self):
        """Сохранение файла"""
        try:
            editor = self.get_current_editor()
            if not editor: return False

            if editor.current_file:
                with open(editor.current_file, 'w', encoding='utf-8') as f:
                    f.write(editor.get_text())
                
                editor.is_modified = False
                self.update_title()
                self.status_label.config(text=f"Файл сохранен: {os.path.basename(editor.current_file)}")
                return True
            else:
                return self.save_as_file()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
            return False
    
    def save_as_file(self):
        """Сохранение файла как..."""
        try:
            editor = self.get_current_editor()
            if not editor: return False

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
                    f.write(editor.get_text())
                
                editor.current_file = filename
                editor.is_modified = False
                self.update_title()
                self.status_label.config(text=f"Файл сохранен: {os.path.basename(filename)}")
                return True
            return False
        except Exception as e:
            print(f"Ошибка сохранения файла как: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
            return False
    
    def check_save_changes(self, editor_to_check):
        """Проверка на несохраненные изменения"""
        try:
            if editor_to_check and editor_to_check.is_modified:
                # Активируем вкладку, чтобы пользователь видел, о каком файле идет речь
                for tab_id, editor in self.editors.items():
                    if editor == editor_to_check:
                        self.notebook.select(tab_id)
                        break

                filename = os.path.basename(editor_to_check.current_file) if editor_to_check.current_file else "Без названия"
                result = messagebox.askyesnocancel(
                    "Несохраненные изменения",
                    f"Сохранить изменения в файле '{filename}'?"
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

    def show_find_dialog(self, replace_mode=False):
        """Показывает диалог поиска/замены"""
        if self.find_window and self.find_window.winfo_exists():
            self.find_window.lift()
            return

        editor = self.get_current_editor()
        if not editor:
            messagebox.showwarning("Внимание", "Нет активного редактора для поиска.")
            return

        self.find_window = FindReplaceDialog(self, editor, replace_mode)

    def go_to_line(self):
        """Переход к указанной строке"""
        editor = self.get_current_editor()
        if not editor:
            return

        try:
            line_count = int(editor.text_area.index(f"{tk.END}-1c").split('.')[0])
            line = simpledialog.askinteger("Перейти к строке", 
                                           f"Введите номер строки (1-{line_count}):",
                                           parent=self, minvalue=1, maxvalue=line_count)
            if line:
                target_pos = f"{line}.0"
                editor.text_area.mark_set(tk.INSERT, target_pos)
                editor.text_area.see(target_pos)
                editor.text_area.focus_set()
                
                line_end_pos = f"{line}.end"
                editor.text_area.tag_remove(tk.SEL, "1.0", tk.END)
                editor.text_area.tag_add(tk.SEL, target_pos, line_end_pos)
        except Exception as e:
            print(f"Ошибка перехода к строке: {e}")
    
    def _proxy_editor_event(self, event_name):
        """Вспомогательный метод для вызова событий в активном редакторе."""
        editor = self.get_current_editor()
        if editor:
            try:
                editor.text_area.event_generate(f'<<{event_name}>>')
            except Exception as e:
                print(f"Ошибка события '{event_name}': {e}")

    # Методы редактирования
    def undo(self): self._proxy_editor_event('Undo')
    def redo(self): self._proxy_editor_event('Redo')
    def cut(self): self._proxy_editor_event('Cut')
    def copy(self): self._proxy_editor_event('Copy')
    def paste(self): self._proxy_editor_event('Paste')
    def select_all(self): self._proxy_editor_event('SelectAll')
    def show_autocomplete(self):
        editor = self.get_current_editor()
        if editor:
            editor.show_autocomplete()
    
    # Методы выполнения кода
    def run_code(self):
        """Запуск всего кода"""
        try:
            editor = self.get_current_editor()
            if not editor:
                self.console.write_warning("Нет открытых файлов для запуска!")
                return

            code = editor.get_text().strip()
            if not code:
                self.console.write_warning("Нет кода для выполнения!")
                return
            
            self.console.clear()
            self.console.write_info("Запуск программы...")
            
            # Сохраняем файл перед запуском, если он не сохранен
            if editor.is_modified and editor.current_file:
                self.save_file()

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
            editor = self.get_current_editor()
            if not editor:
                self.console.write_warning("Нет открытых файлов для запуска!")
                return

            selected_text = editor.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
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
    
    def switch_theme(self):
        """Переключает цветовую тему IDE"""
        new_theme = self.theme_var.get()
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.apply_theme()
            print(f"Тема переключена на: {new_theme}")

    def get_current_editor(self):
        """Возвращает экземпляр CodeEditor для активной вкладки"""
        try:
            if not self.notebook or not self.notebook.tabs():
                return None
            selected_tab_id = self.notebook.select()
            return self.editors.get(selected_tab_id)
        except (tk.TclError, KeyError):
            return None

    def _create_new_tab(self, file_path=None, is_template=False):
        """Создает новую вкладку с редактором"""
        try:
            editor_frame = ttk.Frame(self.notebook)
            editor = CodeEditor(editor_frame, THEMES[self.current_theme])
            editor.frame.pack(fill=tk.BOTH, expand=True)
            
            self.notebook.add(editor_frame, text="Без названия *")
            tab_id = self.notebook.tabs()[-1]
            self.editors[tab_id] = editor
            self.notebook.select(tab_id)
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                editor.set_text(content)
                editor.current_file = file_path
                editor.is_modified = False
            elif is_template:
                self.apply_welcome_template(editor)
                editor.is_modified = False # Шаблон не считается изменением

            self.update_title()
            return editor
        except Exception as e:
            print(f"Ошибка создания новой вкладки: {e}")
            messagebox.showerror("Ошибка", f"Не удалось создать вкладку: {e}")
            return None

    def on_tab_changed(self, event):
        """Обработчик смены активной вкладки"""
        self.update_title()
        self.update_status()

    def on_tab_close_press(self, event):
        """Обрабатывает клик по вкладке для возможного закрытия."""
        try:
            element = self.notebook.identify(event.x, event.y)
            if "close" in element:
                index = self.notebook.index(f"@{event.x},{event.y}")
                tab_id_to_close = self.notebook.tabs()[index]
                editor_to_close = self.editors.get(tab_id_to_close)
                if self.check_save_changes(editor_to_close):
                    self.notebook.forget(tab_id_to_close)
                    if tab_id_to_close in self.editors:
                        del self.editors[tab_id_to_close]
                    self.update_title()
        except tk.TclError:
            pass # Клик не по элементу вкладки
        except Exception as e:
            print(f"Ошибка закрытия вкладки: {e}")

    def apply_theme(self):
        """Применяет текущую цветовую тему ко всем элементам"""
        try:
            colors = THEMES[self.current_theme]
            style = ttk.Style()

            # Настройка стилей ttk
            style.configure('.', background=colors['bg'], foreground=colors['fg'], fieldbackground=colors['editor_bg'])
            style.configure('TFrame', background=colors['bg'])
            style.configure('TPanedWindow', background=colors['bg'])
            
            # Стили для панели инструментов
            style.configure('Toolbar.TFrame', background=colors['toolbar_bg'])
            style.configure('Toolbar.TButton', background=colors['button_bg'], foreground=colors['fg'])
            style.map('Toolbar.TButton', background=[('active', colors['button_active_bg'])])
            style.configure('Toolbar.TLabel', background=colors['toolbar_bg'], foreground=colors['fg'])
            style.configure('Toolbar.TSeparator', background=colors['toolbar_bg'])

            # Стили для строки состояния
            style.configure('Statusbar.TFrame', background=colors['bg'])
            style.configure('Statusbar.TLabel', background=colors['bg'], foreground=colors['fg'])

            # Стили для проводника
            style.configure("Explorer.TFrame", background=colors['bg'])
            style.configure("Treeview", 
                            background=colors['editor_bg'], 
                            foreground=colors['fg'],
                            fieldbackground=colors['editor_bg'],
                            rowheight=22)
            style.map('Treeview', 
                      background=[('selected', colors['select_bg'])],
                      foreground=[('selected', colors['editor_fg'])])
            
            # Стили для вкладок
            style.configure('TNotebook', background=colors['bg']) # Фон за вкладками
            style.configure('TNotebook.Tab', 
                            background=colors['toolbar_bg'], 
                            foreground=colors['fg'], 
                            padding=[5, 2])
            style.map('TNotebook.Tab', 
                      background=[('selected', colors['editor_bg'])],
                      foreground=[('selected', colors['fg'])])
            # Основное окно
            self.config(bg=colors['bg'])
            
            # Компоненты
            self.console.apply_theme(colors)
            for editor in self.editors.values():
                editor.apply_theme(colors)
        except Exception as e:
            print(f"Ошибка применения темы: {e}")
            traceback.print_exc()
    
    def load_settings(self):
        """Загрузка настроек"""
        try:
            settings_file = "dorolang_ide_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.recent_files = settings.get('recent_files', [])
                    self.current_theme = settings.get('theme', 'light')
                    self.last_opened_folder = settings.get('last_opened_folder', None)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            self.recent_files = []
            self.last_opened_folder = None
    
    def save_settings(self):
        """Сохранение настроек"""
        try:
            settings_file = "dorolang_ide_settings.json"
            settings = {
                'recent_files': self.recent_files,
                'theme': self.current_theme,
                'last_opened_folder': self.last_opened_folder
            }
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def show_about(self):
        """О программе"""
        try:
            mode_info = "Полный режим" if DOROLANG_MODULES_OK else "Демо-режим"
            about_text = f"""DoroLang IDE
Режим: {mode_info}

Интегрированная среда разработки 
для языка программирования DoroLang

Автор: Dorofii Karnaukh
Год: 2024-2025

Ключевые возможности:
✅ Полноценный редактор с подсветкой синтаксиса
✅ Работа с несколькими файлами во вкладках
✅ Проводник файлов с управлением (создание/удаление)
✅ Светлая и темная темы оформления
✅ Интерактивная консоль для вывода

DoroLang - простой и мощный язык 
программирования для обучения!"""
            
            messagebox.showinfo("О программе", about_text)
        except Exception as e:
            print(f"Ошибка показа о программе: {e}")
    
    def on_closing(self):
        """Обработчик закрытия приложения"""
        try:
            # Проверяем все открытые вкладки
            for editor in list(self.editors.values()):
                if not self.check_save_changes(editor):
                    return # Пользователь нажал "Отмена"
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
    print("🚀 ЗАПУСК DOROLANG IDE")
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
    sys.exit(main())
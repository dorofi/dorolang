#!/usr/bin/env python3
"""
DoroLang IDE - Main Module

Author: Dorofii Karnaukh
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
    def setup_dorolang_input(self):
        import interpreter
        from tkinter import simpledialog
        def dorolang_input_gui(prompt: str) -> str:
            # Open dialog and return result immediately
            return simpledialog.askstring("Input", prompt, parent=self)
        interpreter.dorolang_input = dorolang_input_gui
    """Main class for enhanced DoroLang IDE"""
    
    def __init__(self):
        super().__init__()
        self.setup_dorolang_input()
        self.setup_fonts()
        try:
            print("Initializing Enhanced DoroLang IDE...")

            self.title("DoroLang IDE")
            self.geometry("1400x900")
            self.minsize(900, 700)
            
            # Check DoroLang modules availability
            # Icons for closing tabs
            # Gray 'x' icon for normal state
            self.img_close = tk.PhotoImage("img_close", data='''R0lGODlhCAAIAPABAJmZmf///yH5BAEAAAEALAAAAAAIAAgAAAIMBIKpqgYhADs=''')
            # Red 'x' icon for active state (hover/press)
            self.img_close_active = tk.PhotoImage("img_close_active", data='''R0lGODlhCAAIAPABAO3t7f///yH5BAEAAAEALAAAAAAIAAgAAAIMBIKpqgYhADs=''')

            # Icon for .doro files
            self.doro_icon = tk.PhotoImage("doro_icon", data='''
                R0lGODlhEAAQAPIAAAAAAP//AP8AAP/9/f//mf//Zv//M///AP/M/wAAAAAAACH5BAEAAAcALAAAAAAQABAAAANKeLrc/jDKSau9OOvNu/9gKI5kaZ5oqq5s675wLM90bd94ru987//AoHBILBqPyKRyyWw6n9CodEqtWq/YrHbL7Xq/4LB4TC6bz+i0es1uu9/wuHxOr9vv+Lx+z+/7/4CBgoOEhYaHiImKi4yNjo+AgZIAAAA7
            ''')
            if DOROLANG_MODULES_OK and Interpreter:
                self.dorolang_interpreter = Interpreter()
                print("✅ Using real DoroLang interpreter")
            else:
                self.dorolang_interpreter = MockInterpreter()
                print("⚠️ Using demo mode (DoroLang modules not loaded)")
            
            # Settings
            self.current_theme = 'light' # Default theme
            self.last_opened_folder = None
            self.notebook = None
            self.find_window = None
            self.editors = {}
            self.recent_files = []
            self.load_settings()
            self.theme_var = tk.StringVar(value=self.current_theme)
            
            # Style setup
            self.setup_style()
            
            # Create components
            print("Creating interface...")
            self.setup_main_area()
            self.setup_menu()
            self.setup_toolbar()
            self.setup_statusbar()
            
            # Apply loaded or default theme
            self.apply_theme()
            
            # Load last opened folder
            if self.last_opened_folder and os.path.isdir(self.last_opened_folder):
                self.file_explorer.populate_tree(self.last_opened_folder)
            
            # Bind events
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.bind_shortcuts()
            
            # Create new file by default with template
            self._create_new_tab(is_template=True)
            
            # Welcome message
            if DOROLANG_MODULES_OK:
                self.console.write_info("Enhanced DoroLang IDE started!")
                self.console.write_info("New features: boolean values, logical operators, conditionals")
                self.console.write_info("Press F5 to run code, Ctrl+Space for autocomplete")
            else:
                self.console.write_warning("IDE started in demo mode.")
                self.console.write_warning("For full functionality, place lexer.py, parser.py, interpreter.py in the same folder.")
            
            print("✅ Enhanced DoroLang IDE successfully initialized!")
            
        except Exception as e:
            print(f"❌ Critical initialization error: {e}")
            traceback.print_exc()
            raise
    
    def bind_shortcuts(self):
        """Binding extended hotkeys"""
        try:
            self.bind('<Control-n>', lambda e: self.new_file())
            self.bind('<Control-o>', lambda e: self.open_file())
            self.bind('<Control-s>', lambda e: self.save_file())
            self.bind('<Control-Shift-S>', lambda e: self.save_as_file())
            self.bind('<Control-w>', lambda e: self.close_current_tab())
            self.bind('<F5>', lambda e: self.run_code())
            self.bind('<F9>', lambda e: self.run_selection())
            self.bind('<Control-t>', lambda e: self.show_template_dialog())
            self.bind('<Control-slash>', lambda e: self.toggle_comment())
            self.bind('<Control-f>', lambda e: self.show_find_dialog(False))
            self.bind('<Control-h>', lambda e: self.show_find_dialog(True))
            self.bind('<Control-g>', lambda e: self.go_to_line())
        except Exception as e:
            print(f"Error binding hotkeys: {e}")
    
    def close_current_tab(self):
        """Closes current tab"""
        try:
            editor = self.get_current_editor()
            if editor and self.check_save_changes(editor):
                tab_id = self.notebook.select()
                self.notebook.forget(tab_id)
                if tab_id in self.editors:
                    del self.editors[tab_id]
                self.update_title()
                
                # If no tabs left, create a new one
                if not self.notebook.tabs():
                    self._create_new_tab(is_template=True)
        except Exception as e:
            print(f"Error closing tab: {e}")
    
    def close_all_tabs(self):
        """Closes all tabs"""
        try:
            editors_to_close = list(self.editors.values())
            for editor in editors_to_close:
                if not self.check_save_changes(editor):
                    return  # User cancelled
            
            # Close all tabs
            for tab_id in list(self.notebook.tabs()):
                self.notebook.forget(tab_id)
            self.editors.clear()
            self.update_title()
            
            # Create a new tab
            self._create_new_tab(is_template=True)
        except Exception as e:
            print(f"Error closing all tabs: {e}")
    
    def setup_style(self):
        """Enhanced style setup"""
        try:
            style = ttk.Style()
            # Use available theme that is easily customizable
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
            print(f"Error setting up styles: {e}")

    def setup_fonts(self):
        """Sets modern fonts for improved appearance."""
        try:
            # Set more modern default font for interface
            default_font = font.nametofont("TkDefaultFont")
            default_font.configure(family="Segoe UI", size=10)

            # For editor and console text, use monospace font
            text_font = font.nametofont("TkTextFont")
            text_font.configure(family="Consolas", size=11)

            print("✅ Modern fonts set (Segoe UI, Consolas).")
        except Exception as e:
            print(f"⚠️ Failed to update fonts: {e}")


    def setup_menu(self):
        """Create extended menu"""
        try:
            menubar = tk.Menu(self)
            self.config(menu=menubar)
            
            # File
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="📁 File", menu=file_menu)
            file_menu.add_command(label="New File (Ctrl+N)", command=self.new_file)
            file_menu.add_command(label="From Template (Ctrl+T)", command=self.show_template_dialog)
            file_menu.add_separator()
            file_menu.add_command(label="Open Folder...", command=self.open_folder)
            file_menu.add_command(label="Open File (Ctrl+O)", command=self.open_file)
            
            # Recent files submenu (will be updated dynamically)
            file_menu.add_separator()
            self.recent_files_menu = tk.Menu(file_menu, tearoff=0)
            file_menu.add_cascade(label="Recent Files", menu=self.recent_files_menu)
            self.update_recent_files_menu()
            
            file_menu.add_separator()
            file_menu.add_command(label="Save (Ctrl+S)", command=self.save_file)
            file_menu.add_command(label="Save As (Ctrl+Shift+S)", command=self.save_as_file)
            file_menu.add_separator()
            file_menu.add_command(label="Close Tab (Ctrl+W)", command=self.close_current_tab)
            file_menu.add_command(label="Close All Tabs", command=self.close_all_tabs)
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.on_closing)
            
            # Edit
            edit_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="✏️ Edit", menu=edit_menu)
            edit_menu.add_command(label="Undo (Ctrl+Z)", command=self.undo)
            edit_menu.add_command(label="Redo (Ctrl+Y)", command=self.redo)
            edit_menu.add_separator()
            edit_menu.add_command(label="Cut (Ctrl+X)", command=self.cut)
            edit_menu.add_command(label="Copy (Ctrl+C)", command=self.copy)
            edit_menu.add_command(label="Paste (Ctrl+V)", command=self.paste)
            edit_menu.add_command(label="Select All (Ctrl+A)", command=self.select_all)
            edit_menu.add_separator()
            edit_menu.add_command(label="Find... (Ctrl+F)", command=lambda: self.show_find_dialog(False))
            edit_menu.add_command(label="Replace... (Ctrl+H)", command=lambda: self.show_find_dialog(True))
            edit_menu.add_command(label="Go to Line... (Ctrl+G)", command=self.go_to_line)
            edit_menu.add_separator()
            edit_menu.add_command(label="Toggle Comment (Ctrl+/)", command=self.toggle_comment)
            edit_menu.add_command(label="Autocomplete (Ctrl+Space)", command=self.show_autocomplete)
            
            # Run
            run_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="▶️ Run", menu=run_menu)
            run_menu.add_command(label="Run Code (F5)", command=self.run_code)
            run_menu.add_command(label="Run Selection (F9)", command=self.run_selection)
            run_menu.add_separator()
            run_menu.add_command(label="Clear Console", command=self.clear_console)
            run_menu.add_command(label="Reset Variables", command=self.reset_interpreter)
            
            # Tools
            tools_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="🔧 Tools", menu=tools_menu)
            tools_menu.add_command(label="Code Templates", command=self.show_template_dialog)
            tools_menu.add_command(label="Check Syntax", command=self.check_syntax)
            tools_menu.add_separator()
            tools_menu.add_command(label="Settings", command=self.show_settings)
            
            # View
            view_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="🎨 View", menu=view_menu)

            theme_menu = tk.Menu(view_menu, tearoff=0)
            view_menu.add_cascade(label="Themes", menu=theme_menu)
            theme_menu.add_radiobutton(label="Light", variable=self.theme_var, value="light", command=self.switch_theme)
            theme_menu.add_radiobutton(label="Dark", variable=self.theme_var, value="dark", command=self.switch_theme)
            
            # Help
            help_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="❓ Help", menu=help_menu)
            help_menu.add_command(label="DoroLang Syntax", command=self.show_syntax_help)
            help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
            help_menu.add_separator()
            help_menu.add_command(label="About", command=self.show_about)
            
        except Exception as e:
            print(f"Error creating menu: {e}")
    
    def setup_toolbar(self):
        """Create enhanced toolbar"""
        try:
            self.toolbar = ttk.Frame(self, style='Toolbar.TFrame')
            toolbar = self.toolbar
            self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
            
            # File buttons
            ttk.Button(toolbar, text="📄 New", command=self.new_file, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="📋 Template", command=self.show_template_dialog, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="📁 Open", command=self.open_file, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="💾 Save", command=self.save_file, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            
            ttk.Separator(toolbar, orient=tk.VERTICAL, style='Toolbar.TSeparator').pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
            # Run buttons
            ttk.Button(toolbar, text="▶️ Run (F5)", command=self.run_code, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="🔄 Selection (F9)", command=self.run_selection, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="🧹 Clear", command=self.clear_console, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            
            ttk.Separator(toolbar, orient=tk.VERTICAL, style='Toolbar.TSeparator').pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
            # Tool buttons
            ttk.Button(toolbar, text="✔️ Syntax", command=self.check_syntax, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="💬 Comment", command=self.toggle_comment, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
            
            ttk.Separator(toolbar, orient=tk.VERTICAL, style='Toolbar.TSeparator').pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
            # Information
            self.line_col_label = ttk.Label(toolbar, text="Line: 1, Column: 1", style='Toolbar.TLabel')
            self.line_col_label.pack(side=tk.RIGHT, padx=5)
            
            # Mode indicator
            mode_text = "Full Mode" if DOROLANG_MODULES_OK else "Demo Mode"
            self.mode_label = ttk.Label(toolbar, text=f"[{mode_text}]", font=("Arial", 8), style='Toolbar.TLabel')
            self.mode_label.pack(side=tk.RIGHT, padx=10)
            
        except Exception as e:
            print(f"Error creating toolbar: {e}")
    
    def setup_main_area(self):
        """Create main work area"""
        try:
            # Main horizontal splitter
            main_paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
            main_paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # 1. File explorer (left)
            self.file_explorer = FileExplorer(main_paned_window, self, doro_icon=self.doro_icon)
            main_paned_window.add(self.file_explorer.frame, weight=1)

            # 2. Right panel (editor + console)
            right_pane = ttk.Frame(main_paned_window)
            main_paned_window.add(right_pane, weight=4)

            # Vertical splitter for editor and console
            editor_console_pane = ttk.PanedWindow(right_pane, orient=tk.VERTICAL)
            editor_console_pane.pack(fill=tk.BOTH, expand=True)
            
            # Tabs for editors
            self.notebook = ttk.Notebook(editor_console_pane, style='TNotebook')
            self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
            self.notebook.bind("<ButtonPress-1>", self.on_tab_close_press)
            editor_console_pane.add(self.notebook, weight=3)
            
            # Console
            self.console = Console(self)
            editor_console_pane.add(self.console.frame, weight=1)
        except Exception as e:
            print(f"Error creating main area: {e}")
            traceback.print_exc()
            raise
    
    def setup_statusbar(self):
        """Create status bar"""
        try:
            self.statusbar = ttk.Frame(self, style='Statusbar.TFrame')
            self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            self.status_label = ttk.Label(self.statusbar, text="Ready", style='Statusbar.TLabel')
            self.status_label.pack(side=tk.LEFT, padx=5)
            
            # Modified indicator
            self.modified_label = ttk.Label(self.statusbar, text="", style='Statusbar.TLabel')
            self.modified_label.pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            print(f"Error creating status bar: {e}")
    
    def apply_welcome_template(self, editor):
        """Applies welcome template to editor"""
        welcome_template = '''# Welcome to DoroLang!
# New features: boolean values, logic, conditionals

say "Hello, DoroLang!"

# Try the new features:
kas name = "Programmer"
kas is_learning = true

if (is_learning) {
    say name + " is learning DoroLang!"
} else {
    say name + " already knows DoroLang"
}
'''
        editor.set_text(welcome_template)
    
    def show_template_dialog(self):
        """Shows template selection dialog"""
        try:
            templates = TemplateManager.get_templates()
            
            # Create dialog window
            dialog = tk.Toplevel(self)
            dialog.title("Code Template Selection")
            dialog.geometry("400x300")
            dialog.transient(self)
            dialog.grab_set()
            
            # Template list
            listbox = tk.Listbox(dialog, font=("Arial", 10))
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for template_name in templates.keys():
                listbox.insert(tk.END, template_name)
            
            # Buttons
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
            
            ttk.Button(button_frame, text="Apply", command=apply_template).pack(side=tk.LEFT)
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
            
            # Auto-select first item
            if templates:
                listbox.selection_set(0)
                listbox.bind('<Double-Button-1>', lambda e: apply_template())
            
        except Exception as e:
            print(f"Template dialog error: {e}")
            messagebox.showerror("Error", f"Failed to open template dialog: {e}")
    
    def toggle_comment(self):
        """Toggles comment for selected lines"""
        try:
            editor = self.get_current_editor()
            if not editor: return

            # Get selected text or current line
            try:
                start_idx = editor.text_area.index(tk.SEL_FIRST)
                end_idx = editor.text_area.index(tk.SEL_LAST)
            except tk.TclError:
                # If no selection, work with current line
                current_line = editor.text_area.index(tk.INSERT).split('.')[0]
                start_idx = f"{current_line}.0"
                end_idx = f"{current_line}.end"
            
            # Get text
            text = editor.text_area.get(start_idx, end_idx)
            lines = text.split('\n')
            
            # Check if we need to add or remove comments
            all_commented = all(line.strip().startswith('#') or line.strip() == '' for line in lines)
            
            # Process each line
            new_lines = []
            for line in lines:
                if all_commented:
                    # Remove comment
                    if line.strip().startswith('#'):
                        # Remove first # and one space after it if present
                        new_line = line.replace('#', '', 1)
                        if new_line.startswith(' '):
                            new_line = new_line[1:]
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)
                else:
                    # Add comment
                    if line.strip():  # Don't comment empty lines
                        new_lines.append('# ' + line)
                    else:
                        new_lines.append(line)
            
            # Replace text
            editor.text_area.delete(start_idx, end_idx)
            editor.text_area.insert(start_idx, '\n'.join(new_lines))
            
        except Exception as e:
            print(f"Error toggling comment: {e}")
    
    def check_syntax(self):
        """Checks syntax without execution"""
        try:
            if not DOROLANG_MODULES_OK:
                self.console.write_warning("Syntax check unavailable in demo mode")
                return
            
            editor = self.get_current_editor()
            if not editor: return

            code = editor.get_text().strip()
            if not code:
                self.console.write_warning("No code to check!")
                return
            
            # Clear previous error highlighting
            editor.text_area.tag_remove("error_line", "1.0", tk.END)
            
            self.console.write_info("Checking syntax...")
            
            try:
                # Only lexer and parser
                lexer = Lexer(code)
                tokens = lexer.tokenize()
                
                parser = Parser(tokens)
                ast = parser.parse()
                
                self.console.write_success(f"Syntax correct! Found {len(ast.statements)} statements")
                
            except LexerError as e:
                error_msg = f"Lexer error at line {e.line}, column {e.column}: {e.message}"
                self.console.write_error(error_msg)
                self._highlight_error_line(editor, e.line)
            except ParseError as e:
                error_msg = f"Syntax error at line {e.token.line}, column {e.token.column}: {e.message}"
                self.console.write_error(error_msg)
                self._highlight_error_line(editor, e.token.line)
            except Exception as e:
                self.console.write_error(f"Unexpected error: {e}")
                
        except Exception as e:
            print(f"Error checking syntax: {e}")
            self.console.write_error(f"Check error: {e}")
    
    def show_syntax_help(self):
        """Shows DoroLang syntax help"""
        help_text = """DoroLang v1.3 - Syntax Help

BASIC CONSTRUCTS:
• say "text"              - output text
• kas variable = value    - declare variable
• input("prompt")         - get user input

DATA TYPES:
• Numbers: 42, 3.14
• Strings: "hello", 'world'
• Booleans: true, false

OPERATORS:
• Arithmetic: +, -, *, /, %
• Comparison: ==, !=, <, >, <=, >=
• Logical: and, or, not

CONDITIONAL CONSTRUCTS:
if (condition) {
    # code if true
} else {
    # code if false
}

COMMENTS:
# This is a comment

EXAMPLES:
kas age = 25
if (age >= 18) {
    say "Adult"
} else {
    say "Minor"
}

kas result = (age > 20) and (age < 30)
say "Age between 20 and 30: " + result

kas name = input("What is your name? ")
say "Hello, " + name + "!"
"""
        messagebox.showinfo("DoroLang Syntax", help_text)
    
    def show_shortcuts(self):
        """Shows keyboard shortcuts"""
        shortcuts_text = """DoroLang IDE Keyboard Shortcuts

FILES:
Ctrl+N        - New file
Ctrl+T        - New from template
Ctrl+O        - Open file
Ctrl+S        - Save
Ctrl+Shift+S  - Save as

EDITING:
Ctrl+Z        - Undo
Ctrl+Y        - Redo
Ctrl+X        - Cut
Ctrl+C        - Copy
Ctrl+V        - Paste
Ctrl+A        - Select all
Ctrl+/        - Comment
Ctrl+Space    - Autocomplete

EXECUTION:
F5            - Run code
F9            - Run selection
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def show_settings(self):
        """Shows settings window"""
        try:
            settings_window = tk.Toplevel(self)
            settings_window.title("IDE Settings")
            settings_window.geometry("500x400")
            settings_window.transient(self)
            settings_window.grab_set()
            
            # Center window
            settings_window.update_idletasks()
            x = self.winfo_x() + (self.winfo_width() // 2) - (settings_window.winfo_width() // 2)
            y = self.winfo_y() + (self.winfo_height() // 2) - (settings_window.winfo_height() // 2)
            settings_window.geometry(f"+{x}+{y}")
            
            # Settings frame
            main_frame = ttk.Frame(settings_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Theme selection
            ttk.Label(main_frame, text="Color Theme:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
            theme_frame = ttk.Frame(main_frame)
            theme_frame.pack(fill=tk.X, pady=(0, 15))
            
            theme_var = tk.StringVar(value=self.current_theme)
            ttk.Radiobutton(theme_frame, text="Light", variable=theme_var, value="light").pack(side=tk.LEFT, padx=10)
            ttk.Radiobutton(theme_frame, text="Dark", variable=theme_var, value="dark").pack(side=tk.LEFT, padx=10)
            
            # Editor settings
            ttk.Label(main_frame, text="Editor Settings:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
            
            # Font size
            font_frame = ttk.Frame(main_frame)
            font_frame.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(font_frame, text="Font Size:").pack(side=tk.LEFT)
            font_size_var = tk.StringVar(value="11")
            font_size_combo = ttk.Combobox(font_frame, textvariable=font_size_var, values=["9", "10", "11", "12", "14", "16"], width=10, state="readonly")
            font_size_combo.pack(side=tk.LEFT, padx=5)
            
            # Auto-save
            auto_save_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(main_frame, text="Auto-save before running", variable=auto_save_var).pack(anchor=tk.W, pady=5)
            
            # Show line numbers
            show_line_nums_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(main_frame, text="Show line numbers", variable=show_line_nums_var).pack(anchor=tk.W, pady=5)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(20, 0))
            
            def apply_settings():
                # Apply theme
                if theme_var.get() != self.current_theme:
                    self.current_theme = theme_var.get()
                    self.theme_var.set(self.current_theme)
                    self.apply_theme()
                
                # Save settings
                self.save_settings()
                settings_window.destroy()
                messagebox.showinfo("Settings", "Settings saved successfully!")
            
            ttk.Button(button_frame, text="Apply", command=apply_settings).pack(side=tk.RIGHT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.RIGHT)
            
        except Exception as e:
            print(f"Error showing settings: {e}")
            messagebox.showerror("Error", f"Failed to open settings: {e}")
    
    def update_status(self):
        """Обновление строки состояния"""
        try:
            editor = self.get_current_editor()
            if editor:
                cursor_pos = editor.get_cursor_position()
                line, col = cursor_pos.split('.')
                self.line_col_label.config(text=f"Line: {line}, Column: {int(col) + 1}")
            else:
                self.line_col_label.config(text="")
        except Exception as e:
            print(f"Ошибка обновления статуса: {e}")
    
    def update_title(self):
        """Обновление заголовка окна"""
        try:
            editor = self.get_current_editor()
            if editor:
                filename = os.path.basename(editor.current_file) if editor.current_file else "Untitled"
                modified_mark = " *" if editor.is_modified else ""
                # Update tab text
                tab_id = self.notebook.select()
                self.notebook.tab(tab_id, text=f"{filename}{modified_mark} ") # Space for offset from close button
            else:
                filename = "No open files"
                modified_mark = ""

            theme_name = self.current_theme.capitalize()
            self.title(f"DoroLang IDE ({theme_name}) - {filename}{modified_mark}")
        except Exception as e:
            print(f"Ошибка обновления заголовка: {e}")
    
    # File operations methods
    def new_file(self):
        """Create new file"""
        try:
            self._create_new_tab()
            self.status_label.config(text="New file created")
        except Exception as e:
            print(f"Error creating new file: {e}")
            messagebox.showerror("Error", f"Failed to create new file: {e}")

    def open_folder(self):
        """Open folder in explorer"""
        try:
            path = filedialog.askdirectory(title="Select Project Folder")
            if path:
                self.file_explorer.populate_tree(path)
                self.last_opened_folder = path
                self.status_label.config(text=f"Folder opened: {os.path.basename(path)}")
        except Exception as e:
            print(f"Error opening folder: {e}")
            messagebox.showerror("Error", f"Failed to open folder: {e}")

    def open_file_from_path(self, path):
        """Open file by specified path (for explorer)"""
        try:
            # Check if file is already open
            for tab_id, editor in self.editors.items():
                if editor.current_file == path:
                    self.notebook.select(tab_id)
                    return
            
            # If not open, create new tab
            self._create_new_tab(file_path=path)
            self.status_label.config(text=f"File opened: {os.path.basename(path)}")
        except Exception as e:
            print(f"Error opening file by path: {e}")
            messagebox.showerror("Error", f"Failed to open file: {e}")
    
    def open_file(self):
        """Open file"""
        try:
            filename = filedialog.askopenfilename(
                title="Open DoroLang File",
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
        """Save file"""
        try:
            editor = self.get_current_editor()
            if not editor: return False

            if editor.current_file:
                with open(editor.current_file, 'w', encoding='utf-8') as f:
                    f.write(editor.get_text())
                
                editor.is_modified = False
                self.update_title()
                self.status_label.config(text=f"File saved: {os.path.basename(editor.current_file)}")
                return True
            else:
                return self.save_as_file()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
            return False
    
    def save_as_file(self):
        """Save file as..."""
        try:
            editor = self.get_current_editor()
            if not editor: return False

            filename = filedialog.asksaveasfilename(
                title="Save DoroLang File",
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
                self.status_label.config(text=f"File saved: {os.path.basename(filename)}")
                return True
            return False
        except Exception as e:
            print(f"Error saving file as: {e}")
            messagebox.showerror("Error", f"Failed to save file: {e}")
            return False
    
    def check_save_changes(self, editor_to_check):
        """Check for unsaved changes"""
        try:
            if editor_to_check and editor_to_check.is_modified:
                # Activate tab so user can see which file is being discussed
                for tab_id, editor in self.editors.items():
                    if editor == editor_to_check:
                        self.notebook.select(tab_id)
                        break

                filename = os.path.basename(editor_to_check.current_file) if editor_to_check.current_file else "Untitled"
                result = messagebox.askyesnocancel(
                    "Unsaved Changes",
                    f"Save changes in file '{filename}'?"
                )
                if result is True:
                    return self.save_file()
                elif result is False:
                    return True
                else:  # Cancel
                    return False
            return True
        except Exception as e:
            print(f"Error checking changes: {e}")
            return True

    def show_find_dialog(self, replace_mode=False):
        """Показывает диалог поиска/замены"""
        if self.find_window and self.find_window.winfo_exists():
            self.find_window.lift()
            return

        editor = self.get_current_editor()
        if not editor:
            messagebox.showwarning("Warning", "No active editor for search.")
            return

        self.find_window = FindReplaceDialog(self, editor, replace_mode)

    def go_to_line(self):
        """Go to specified line"""
        editor = self.get_current_editor()
        if not editor:
            return

        try:
            line_count = int(editor.text_area.index(f"{tk.END}-1c").split('.')[0])
            line = simpledialog.askinteger("Go to Line", 
                                           f"Enter line number (1-{line_count}):",
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
            print(f"Error going to line: {e}")
    
    def _proxy_editor_event(self, event_name):
        """Helper method to trigger events in active editor."""
        editor = self.get_current_editor()
        if editor:
            try:
                editor.text_area.event_generate(f'<<{event_name}>>')
            except Exception as e:
                print(f"Event error '{event_name}': {e}")

    # Editing methods
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
    
    def execute_interactive_line(self, command):
        """Выполняет одну строку кода из интерактивной консоли."""
        try:
            if not DOROLANG_MODULES_OK:
                self.console.write_warning("Interactive console unavailable in demo mode.")
                return

            # Display entered command
            self.console.write(f">>> {command}\n", "input")

            # Check for special commands
            if command.strip().lower() == 'clear':
                self.clear_console()
                return
            if command.strip().lower() == 'reset':
                self.reset_interpreter()
                return

            # "Smart" execution: if it doesn't look like a statement, treat it as an expression for output
            is_statement = re.match(r'^\s*(say|kas|if)', command)
            code_to_run = command if is_statement else f'say {command}'

            # Запускаем в потоке, чтобы не блокировать GUI
            thread = threading.Thread(target=self._execute_code, args=(code_to_run, True)) # True for interactive
            thread.daemon = True
            thread.start()

        except Exception as e:
            self.console.write_error(f"Interactive execution error: {e}")
            print(f"Interactive execution error: {e}")
            traceback.print_exc()

    # Code execution methods
    def run_code(self):
        """Запуск всего кода"""
        try:
            editor = self.get_current_editor()
            if not editor:
                self.console.write_warning("No open files to run!")
                return

            code = editor.get_text().strip()
            if not code:
                self.console.write_warning("No code to execute!")
                return
            
            self.console.clear()
            self.console.write_info("Running program...")
            
            # Auto-save before running if file is modified
            if editor.is_modified and editor.current_file:
                try:
                    with open(editor.current_file, 'w', encoding='utf-8') as f:
                        f.write(editor.get_text())
                    editor.is_modified = False
                    self.update_title()
                except Exception as e:
                    self.console.write_warning(f"Auto-save failed: {e}")

            # Run through after to avoid blocking main thread and work correctly with dialogs
            self.after(0, lambda: self._execute_code(code, False))
            
        except Exception as e:
            print(f"Error running code: {e}")
            self.console.write_error(f"Error running: {e}")
    
    def run_selection(self):
        """Запуск выделенного кода"""
        try:
            editor = self.get_current_editor()
            if not editor:
                self.console.write_warning("No open files to run!")
                return

            selected_text = editor.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text.strip():
                self.console.clear()
                self.console.write_info("Running selected code...")
                
                thread = threading.Thread(target=self._execute_code, args=(selected_text, False))
                thread.daemon = True
                thread.start()
            else:
                self.console.write_warning("No selected text!")
        except tk.TclError:
            self.console.write_warning("No selected text!")
        except Exception as e:
            print(f"Error running selection: {e}")
            self.console.write_error(f"Error running selection: {e}")
    
    def _execute_code(self, code, interactive=False):
        """Execute DoroLang code. interactive=True for REPL mode."""
        try:
            if not DOROLANG_MODULES_OK:
                # Demo mode
                output = self.dorolang_interpreter.interpret(code)
                for line in output:
                    self.console.write(line + "\n", "warning")
                return
            
            # Create DoroLang component instances
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Execute code
            output = self.dorolang_interpreter.interpret(ast)
            
            # Output result
            if output:
                for line in output:
                    # In interactive mode, don't show error icon as it's already in tag
                    if "❌" in line and not interactive:
                        self.console.write(line + "\n", "error")
                    else:
                        # Remove icon as tag already exists
                        clean_line = line.replace("❌ ", "") if "❌" in line else line
                        self.console.write(clean_line + "\n", "output")
            
            # In interactive mode, don't show statistics to avoid cluttering output
            if not interactive:
                variables = self.dorolang_interpreter.get_variables()
                if variables:
                    self.console.write_info(f"Variables in memory: {len(variables)}")
                self.console.write_success("Execution completed!")
            
        except Exception as e:
            editor = self.get_current_editor()
            
            if DOROLANG_MODULES_OK:
                if isinstance(e, LexerError):
                    error_msg = f"Lexer error at line {e.line}, column {e.column}: {e.message}"
                    self.console.write_error(error_msg)
                    if editor:
                        self._highlight_error_line(editor, e.line)
                elif isinstance(e, ParseError):
                    error_msg = f"Syntax error at line {e.token.line}, column {e.token.column}: {e.message}"
                    self.console.write_error(error_msg)
                    if editor:
                        self._highlight_error_line(editor, e.token.line)
                elif isinstance(e, DoroRuntimeError):
                    self.console.write_error(f"Runtime error: {e.message}")
                else:
                    self.console.write_error(f"Unexpected error: {e}")
            else:
                self.console.write_error(f"Execution error: {e}")
            
            print(f"Error executing code: {e}")
            traceback.print_exc()
    
    def _highlight_error_line(self, editor, line_number):
        """Highlights error line in editor"""
        try:
            # Remove previous error highlighting
            editor.text_area.tag_remove("error_line", "1.0", tk.END)
            
            # Highlight error line
            line_start = f"{line_number}.0"
            line_end = f"{line_number}.end"
            editor.text_area.tag_add("error_line", line_start, line_end)
            editor.text_area.tag_config("error_line", background="#ffcccc")
            
            # Scroll to error line
            editor.text_area.see(line_start)
        except Exception as e:
            print(f"Error highlighting line: {e}")
    
    def clear_console(self):
        """Clear console"""
        try:
            self.console.clear()
            self.console.write_info("Console cleared")
        except Exception as e:
            print(f"Error clearing console: {e}")
    
    def reset_interpreter(self):
        """Reset interpreter"""
        try:
            self.dorolang_interpreter.reset()
            self.console.clear()
            self.console.write_info("Interpreter variables reset")
        except Exception as e:
            print(f"Error resetting interpreter: {e}")
            self.console.write_error(f"Reset error: {e}")
    
    def switch_theme(self):
        """Switches IDE color theme"""
        new_theme = self.theme_var.get()
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.apply_theme()
            print(f"Theme switched to: {new_theme}")

    def update_recent_files_menu(self):
        """Updates recent files menu"""
        try:
            self.recent_files_menu.delete(0, tk.END)
            if self.recent_files:
                # Filter existing files
                existing_files = [f for f in self.recent_files[:10] if os.path.exists(f)]
                if existing_files:
                    for file_path in existing_files:
                        self.recent_files_menu.add_command(
                            label=os.path.basename(file_path),
                            command=lambda path=file_path: self.open_file_from_path(path)
                        )
                else:
                    self.recent_files_menu.add_command(label="(No recent files)", state=tk.DISABLED)
            else:
                self.recent_files_menu.add_command(label="(No recent files)", state=tk.DISABLED)
        except Exception as e:
            print(f"Error updating recent files menu: {e}")
    
    def get_current_editor(self):
        """Returns CodeEditor instance for active tab"""
        try:
            if not self.notebook or not self.notebook.tabs():
                return None
            selected_tab_id = self.notebook.select()
            return self.editors.get(selected_tab_id)
        except (tk.TclError, KeyError):
            return None

    def _create_new_tab(self, file_path=None, is_template=False):
        """Creates new tab with editor"""
        try:
            editor_frame = ttk.Frame(self.notebook)
            editor = CodeEditor(editor_frame, THEMES[self.current_theme])
            editor.frame.pack(fill=tk.BOTH, expand=True)
            
            self.notebook.add(editor_frame, text="Untitled *")
            tab_id = self.notebook.tabs()[-1]
            self.editors[tab_id] = editor
            self.notebook.select(tab_id)
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                editor.set_text(content)
                editor.current_file = file_path
                editor.is_modified = False
                
                # Add to recent files
                if file_path in self.recent_files:
                    self.recent_files.remove(file_path)
                self.recent_files.insert(0, file_path)
                self.recent_files = self.recent_files[:20]  # Keep max 20 recent files
                self.update_recent_files_menu()
                self.save_settings()
            elif is_template:
                self.apply_welcome_template(editor)
                editor.is_modified = False # Template doesn't count as modification

            self.update_title()
            return editor
        except Exception as e:
            print(f"Error creating new tab: {e}")
            messagebox.showerror("Error", f"Failed to create tab: {e}")
            return None

    def on_tab_changed(self, event):
        """Handler for active tab change"""
        self.update_title()
        self.update_status()

    def on_tab_close_press(self, event):
        """Handles tab click for possible closing."""
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
            pass # Click not on tab element
        except Exception as e:
            print(f"Error closing tab: {e}")

    def apply_theme(self):
        """Applies current color theme to all elements"""
        try:
            colors = THEMES[self.current_theme]
            style = ttk.Style()

            # Configure ttk styles
            style.configure('.', background=colors['bg'], foreground=colors['fg'], fieldbackground=colors['editor_bg'])
            style.configure('TFrame', background=colors['bg'])
            style.configure('TPanedWindow', background=colors['bg'])
            
            # Toolbar styles
            style.configure('Toolbar.TFrame', background=colors['toolbar_bg'])
            style.configure('Toolbar.TButton', background=colors['button_bg'], foreground=colors['fg'])
            style.map('Toolbar.TButton', background=[('active', colors['button_active_bg'])])
            style.configure('Toolbar.TLabel', background=colors['toolbar_bg'], foreground=colors['fg'])
            style.configure('Toolbar.TSeparator', background=colors['toolbar_bg'])

            # Status bar styles
            style.configure('Statusbar.TFrame', background=colors['bg'])
            style.configure('Statusbar.TLabel', background=colors['bg'], foreground=colors['fg'])

            # Explorer styles
            style.configure("Explorer.TFrame", background=colors['bg'])
            style.configure("Treeview", 
                            background=colors['editor_bg'], 
                            foreground=colors['fg'],
                            fieldbackground=colors['editor_bg'],
                            rowheight=22)
            style.map('Treeview', 
                      background=[('selected', colors['select_bg'])],
                      foreground=[('selected', colors['editor_fg'])])
            
            # Tab styles
            style.configure('TNotebook', background=colors['bg']) # Background behind tabs
            style.configure('TNotebook.Tab', 
                            background=colors['toolbar_bg'], 
                            foreground=colors['fg'], 
                            padding=[5, 2])
            style.map('TNotebook.Tab', 
                      background=[('selected', colors['editor_bg'])],
                      foreground=[('selected', colors['fg'])])
            # Main window
            self.config(bg=colors['bg'])
            
            # Components
            self.console.apply_theme(colors)
            for editor in self.editors.values():
                editor.apply_theme(colors)
        except Exception as e:
            print(f"Error applying theme: {e}")
            traceback.print_exc()
    
    def load_settings(self):
        """Load settings"""
        try:
            settings_file = "dorolang_ide_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.recent_files = settings.get('recent_files', [])
                    self.current_theme = settings.get('theme', 'light')
                    self.last_opened_folder = settings.get('last_opened_folder', None)
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.recent_files = []
            self.last_opened_folder = None
    
    def save_settings(self):
        """Save settings"""
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
            print(f"Error saving settings: {e}")
    
    def show_about(self):
        """About"""
        try:
            mode_info = "Full Mode" if DOROLANG_MODULES_OK else "Demo Mode"
            about_text = f"""DoroLang IDE
Mode: {mode_info}

Integrated Development Environment 
for DoroLang Programming Language

Author: Dorofii Karnaukh
Year: 2024-2025

Key Features:
✅ Full-featured editor with syntax highlighting
✅ Multi-file support with tabs
✅ File explorer with management (create/delete)
✅ Light and dark themes
✅ Interactive output console

DoroLang - simple and powerful programming 
language for learning!"""
            
            messagebox.showinfo("About", about_text)
        except Exception as e:
            print(f"Ошибка показа о программе: {e}")
    
    def on_closing(self):
        """Application close handler"""
        try:
            # Check all open tabs
            for editor in list(self.editors.values()):
                if not self.check_save_changes(editor):
                    return # User pressed "Cancel"
            self.save_settings()
            self.destroy()
        except Exception as e:
            print(f"Error closing application: {e}")
            self.destroy()  # Force close
    
    def run(self):
        """Run IDE"""
        try:
            print("Starting main application loop...")
            self.mainloop()
        except Exception as e:
            print(f"Main loop error: {e}")
            traceback.print_exc()


def main():
    """Main function to launch Enhanced DoroLang IDE"""
    
    print("=" * 60)
    print("🚀 LAUNCHING DOROLANG IDE")
    print("=" * 60)
    
    try:
        # --- INTERFACE QUALITY IMPROVEMENT (DPI AWARENESS) ---
        # This makes the application "aware" of screen scaling in Windows.
        # As a result, text and interface elements are no longer blurry on displays
        # with scaling greater than 100% (e.g., 125% or 150%).
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
                print("✅ DPI-awareness set for clear rendering on Windows.")
            except (ImportError, AttributeError):
                print("⚠️ Failed to set DPI-awareness (ctypes module or function not found).")
        # --- END IMPROVEMENT ---

        # System diagnostics
        print(f"Python version: {sys.version}")
        print(f"Working directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        
        # Check tkinter
        try:
            import tkinter
            print("✅ Tkinter available")
        except ImportError as e:
            print(f"❌ Tkinter unavailable: {e}")
            return
        
        # Create and run IDE
        print("\nCreating Enhanced IDE instance...")
        ide = DoroLangIDE()
        
        print("Enhanced IDE created successfully, starting...")
        ide.run()
        
        print("Enhanced IDE finished.")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        print("\nFull error traceback:")
        traceback.print_exc()
        
        # Show error window if possible
        try:
            import tkinter.messagebox as mb
            error_details = f"""Critical error launching Enhanced IDE:

Error: {str(e)}

Details:
- Python: {sys.version}
- Working directory: {os.getcwd()}
- DoroLang modules: {'✅ OK' if DOROLANG_MODULES_OK else '❌ Not loaded'}

Check:
1. Are all required files in the folder?
2. Are all dependencies installed?
3. Console output for details

Full traceback printed to console."""
            
            mb.showerror("Critical Error Enhanced DoroLang IDE", error_details)
        except:
            pass  # Even if messagebox doesn't work
        
        print(f"\n💡 Possible solutions:")
        print("1. Make sure lexer.py, parser.py, interpreter.py are in the same folder")
        print("2. Check file permissions")  
        print("3. Try running from command line: python dorolang_ide.py")
        print("4. Check Python version (3.6+ required)")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
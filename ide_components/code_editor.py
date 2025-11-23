import tkinter as tk
from tkinter import scrolledtext
import re
import traceback

class SyntaxHighlighter:
    """Enhanced syntax highlighting for DoroLang with support for new features"""
    
    def __init__(self, text_widget, initial_colors):
        self.text_widget = text_widget
        self.colors = initial_colors
        self.setup_tags()
        self.compile_regex()
        self.highlight_job = None

    def setup_tags(self):
        """Setup tags for highlighting"""
        base_font = ("Consolas", 11)
        bold_font = (base_font[0], base_font[1], "bold")
        italic_font = (base_font[0], base_font[1], "italic")

        try:
            self.text_widget.tag_config("keyword", foreground=self.colors['keyword'], font=bold_font)
            self.text_widget.tag_config("input", foreground="#A259FF", font=bold_font)  # Purple
            self.text_widget.tag_config("logical", foreground=self.colors['logical'], font=bold_font)
            self.text_widget.tag_config("boolean", foreground=self.colors['boolean'], font=bold_font)
            self.text_widget.tag_config("string", foreground=self.colors['string'])
            self.text_widget.tag_config("number", foreground=self.colors['number'])
            self.text_widget.tag_config("comment", foreground=self.colors['comment'], font=italic_font)
            self.text_widget.tag_config("operator", foreground=self.colors['operator'])
            self.text_widget.tag_config("delimiter", foreground=self.colors['delimiter'])
        except Exception as e:
            print(f"Warning: Error setting up highlight tags: {e}")
    
    def compile_regex(self):
        """Compile regular expression with support for new tokens"""
        keywords = ['say', 'kas', 'if', 'else', 'while', 'for', 'function', 'return', 'input', 'to', 'step']
        logical_ops = ['and', 'or', 'not']
        boolean_values = ['true', 'false']

        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        input_pattern = r'\binput\b'
        logical_pattern = r'\b(' + '|'.join(logical_ops) + r')\b'
        boolean_pattern = r'\b(' + '|'.join(boolean_values) + r')\b'

        token_patterns = [
            ('COMMENT', r'#.*$'),
            ('STRING', r'(\".*?\"|\'.*?\')'),
            ('NUMBER', r'\b\d+\.?\d*\b'),
            ('BOOLEAN', boolean_pattern),
            ('LOGICAL', logical_pattern),
            ('INPUT', input_pattern),
            ('KEYWORD', keyword_pattern),
            ('OPERATOR', r'==|!=|<=|>=|[+\-*/%=<>]'),
            ('DELIMITER', r'[(){}]'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('MISMATCH', r'.')
        ]

        self.regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_patterns))

    def highlight(self):
        """Starts delayed syntax highlighting"""
        if self.highlight_job:
            self.text_widget.after_cancel(self.highlight_job)
        self.highlight_job = self.text_widget.after(100, self.apply_highlight)

    def apply_theme(self, colors):
        """Applies new color scheme"""
        self.colors = colors
        self.setup_tags()
        self.highlight()

    def apply_highlight(self):
        """Applies enhanced syntax highlighting to entire text"""
        try:
            tags_to_remove = ["keyword", "logical", "boolean", "string", "number", "comment", "operator", "delimiter", "input"]
            for tag in tags_to_remove:
                self.text_widget.tag_remove(tag, "1.0", tk.END)

            content = self.text_widget.get("1.0", tk.END)

            for line_num, line in enumerate(content.splitlines(), 1):
                for match in self.regex.finditer(line):
                    kind = match.lastgroup
                    tag_name = kind.lower() if kind else None
                    if tag_name in tags_to_remove:
                        start = match.start()
                        end = match.end()
                        start_index = f"{line_num}.{start}"
                        end_index = f"{line_num}.{end}"
                        self.text_widget.tag_add(tag_name, start_index, end_index)

        except Exception as e:
            print(f"Ошибка подсветки синтаксиса: {e}")


class AutocompleteWindow(tk.Toplevel):
    """Dropdown window for autocomplete"""
    def __init__(self, parent, matches, completion_callback, close_callback):
        super().__init__(parent)
        self.completion_callback = completion_callback
        self.close_callback = close_callback
        
        self.overrideredirect(True)

        self.listbox = tk.Listbox(self, exportselection=False, font=("Consolas", 10))
        self.listbox.pack(fill=tk.BOTH, expand=True)

        for item in matches:
            self.listbox.insert(tk.END, item)
        
        if matches:
            self.listbox.selection_set(0)

        self.listbox.bind("<Double-Button-1>", self.on_select)
        self.listbox.bind("<Return>", self.on_select)
        self.listbox.bind("<Escape>", lambda e: self.destroy())
        self.bind("<FocusOut>", lambda e: self.destroy())

    def on_select(self, event=None):
        if self.listbox.curselection():
            value = self.listbox.get(self.listbox.curselection())
            self.completion_callback(value)
        self.destroy()

class CodeEditor:
    """Enhanced code editor with autocomplete support"""
    
    def __init__(self, parent, initial_colors):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.current_file = None
        self.is_modified = False
        self.colors = initial_colors
        self.autocomplete_window = None
        self.setup_editor()
    
    def setup_editor(self):
        """Setup editor"""
        try:
            editor_frame = tk.Frame(self.frame)
            editor_frame.pack(fill=tk.BOTH, expand=True)
            
            self.line_frame = tk.Frame(editor_frame, width=50)
            self.line_frame.pack(side=tk.LEFT, fill=tk.Y)
            
            self.line_numbers = tk.Text(self.line_frame, width=4, padx=3, pady=3,
                                       state=tk.DISABLED,
                                       wrap=tk.NONE, font=("Consolas", 11))
            self.line_numbers.pack(fill=tk.BOTH, expand=True)
            
            self.text_area = scrolledtext.ScrolledText(
                editor_frame,
                wrap=tk.NONE,
                font=("Consolas", 11),
                undo=True,
                maxundo=50,
                insertwidth=2
            )
            self.text_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            
            self.highlighter = SyntaxHighlighter(self.text_area, self.colors)
            
            self.text_area.bind('<KeyRelease>', self.on_key_release)
            self.text_area.bind('<Button-1>', self.on_click)
            self.text_area.bind('<MouseWheel>', self.on_mousewheel)
            self.text_area.bind('<<Modified>>', self.on_modified)
            self.text_area.bind('<Control-space>', self.show_autocomplete)

            # Tag for bracket highlighting
            self.text_area.tag_configure("match")
            
            # Tag for error line highlighting
            self.text_area.tag_configure("error_line", background="#ffcccc")
            
            self.text_area.config(yscrollcommand=self.sync_scroll)
            
            self.update_line_numbers()
            self.apply_theme(self.colors)
            
        except Exception as e:
            print(f"Error setting up editor: {e}")
            traceback.print_exc()
            raise

    def apply_theme(self, colors):
        """Applies new color scheme to editor"""
        self.colors = colors
        self.text_area.config(
            background=colors['editor_bg'],
            foreground=colors['editor_fg'],
            selectbackground=colors['select_bg'],
            insertbackground=colors['insert_bg']
        )
        self.line_numbers.config(
            background=colors['line_num_bg'],
            foreground=colors['line_num_fg']
        )
        self.text_area.tag_configure("match", background=colors.get('match_bg', 'yellow'), foreground=colors.get('match_fg', 'black'))
        self.line_frame.config(background=colors['line_num_bg'])
        self.highlighter.apply_theme(colors)
    
    def show_autocomplete(self, event=None):
        """Shows autocomplete dropdown list with keywords and variables"""
        self._close_autocomplete()
        try:
            keywords = ['say', 'kas', 'if', 'else', 'while', 'for', 'function', 'return', 'true', 'false', 'and', 'or', 'not', 'input', 'to', 'step']
            
            # Extract variables from current file
            all_text = self.text_area.get("1.0", tk.END)
            variable_pattern = r'\bkas\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*='
            variables = list(set(re.findall(variable_pattern, all_text)))
            
            current_pos = self.text_area.index(tk.INSERT)
            line_start = current_pos.rsplit('.', 1)[0] + '.0'
            line_text = self.text_area.get(line_start, current_pos)
            
            words = re.findall(r'\w+', line_text)
            if words:
                self.partial_word = words[-1]
                
                # Match both keywords and variables
                keyword_matches = [kw for kw in keywords if kw.startswith(self.partial_word)]
                variable_matches = [var for var in variables if var.startswith(self.partial_word)]
                
                # Combine and sort (keywords first, then variables)
                matches = keyword_matches + variable_matches
                
                if matches:
                    if len(matches) == 1 and matches[0] == self.partial_word:
                        return

                    x, y, _, height = self.text_area.bbox(tk.INSERT)
                    x += self.text_area.winfo_rootx()
                    y += self.text_area.winfo_rooty() + height

                    self.autocomplete_window = AutocompleteWindow(self.parent, matches, self._insert_completion, self._close_autocomplete)
                    self.autocomplete_window.geometry(f"+{x}+{y}")
                    self.autocomplete_window.listbox.focus_set()
        except Exception as e:
            print(f"Autocomplete error: {e}")

    def _insert_completion(self, value):
        """Inserts selected word"""
        try:
            start_pos = self.text_area.index(f"{tk.INSERT} - {len(self.partial_word)} chars")
            self.text_area.delete(start_pos, tk.INSERT)
            self.text_area.insert(tk.INSERT, value)
        except Exception as e:
            print(f"Ошибка вставки автодополнения: {e}")
        finally:
            self._close_autocomplete()

    def _close_autocomplete(self, event=None):
        if self.autocomplete_window:
            self.autocomplete_window.destroy()
            self.autocomplete_window = None
    
    def sync_scroll(self, *args):
        """Synchronize scrolling of line numbers and text"""
        try:
            self.line_numbers.yview_moveto(args[0])
            if hasattr(self.text_area, 'vbar'):
                self.text_area.vbar.set(*args)
        except Exception as e:
            print(f"Ошибка синхронизации прокрутки: {e}")
    
    def on_key_release(self, event=None):
        """Update after key press"""
        try:
            self._close_autocomplete()
            self.update_line_numbers()
            self.highlight_matching_bracket()
            self.highlighter.highlight()
            if hasattr(self.parent, 'update_status'):
                self.parent.update_status()
        except Exception as e:
            print(f"Ошибка обработки нажатия клавиши: {e}")
    
    def on_click(self, event=None):
        """Update after mouse click"""
        try:
            self._close_autocomplete()
            self.update_line_numbers()
            self.highlight_matching_bracket()
            if hasattr(self.parent, 'update_status'):
                self.parent.update_status()
        except Exception as e:
            print(f"Ошибка обработки клика: {e}")
    
    def on_mousewheel(self, event=None):
        """Synchronize when scrolling with wheel"""
        try:
            self.text_area.yview_scroll(int(-1 * (event.delta / 120)), "units")
            self._close_autocomplete()
            return "break"
        except Exception as e:
            print(f"Ошибка прокрутки: {e}")
    
    def on_modified(self, event=None):
        """Text change handler"""
        try:
            if not self.is_modified:
                self.is_modified = True
                if hasattr(self.parent, 'update_title'):
                    self.parent.update_title()
        except Exception as e:
            print(f"Ошибка обработки изменений: {e}")
    
    def update_line_numbers(self):
        """Update line numbers"""
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
        """Get all text"""
        try:
            return self.text_area.get("1.0", tk.END + "-1c")
        except Exception as e:
            print(f"Ошибка получения текста: {e}")
            return ""
    
    def set_text(self, text):
        """Set text"""
        try:
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", text)
            self.update_line_numbers()
            self.highlighter.highlight()
            self.is_modified = False
        except Exception as e:
            print(f"Ошибка установки текста: {e}")
    
    def get_cursor_position(self):
        """Get cursor position"""
        try:
            return self.text_area.index(tk.INSERT)
        except Exception as e:
            print(f"Ошибка получения позиции курсора: {e}")
            return "1.0"

    def highlight_matching_bracket(self, event=None):
        """Highlight matching brackets"""
        self.text_area.tag_remove("match", "1.0", tk.END)

        cursor_pos = self.text_area.index(tk.INSERT)
        
        # Check character before cursor
        char_before = self.text_area.get(f"{cursor_pos}-1c", cursor_pos)
        
        # Check character after cursor
        char_after = self.text_area.get(cursor_pos, f"{cursor_pos}+1c")

        brackets = {'(': ')', '[': ']', '{': '}', ')': '(', ']': '[', '}': '{'}

        if char_before in "()[]{}":
            match_pos = self._find_bracket_match(f"{cursor_pos}-1c", brackets[char_before])
            if match_pos:
                self.text_area.tag_add("match", f"{cursor_pos}-1c", cursor_pos)
                self.text_area.tag_add("match", match_pos, f"{match_pos}+1c")
        elif char_after in "()[]{}":
            match_pos = self._find_bracket_match(cursor_pos, brackets[char_after])
            if match_pos:
                self.text_area.tag_add("match", cursor_pos, f"{cursor_pos}+1c")
                self.text_area.tag_add("match", match_pos, f"{match_pos}+1c")

    def _find_bracket_match(self, start_pos, match_char):
        """Finds matching bracket"""
        start_char = self.text_area.get(start_pos, f"{start_pos}+1c")
        
        if start_char in "([{": # Search forward
            direction = 1
            end_pos = tk.END
            current_pos = f"{start_pos}+1c"
        elif start_char in ")]}": # Search backward
            direction = -1
            end_pos = "1.0"
            current_pos = f"{start_pos}-1c"
        else:
            return None

        balance = 1
        while True:
            if direction == 1 and self.text_area.compare(current_pos, ">=", end_pos): break
            if direction == -1 and self.text_area.compare(current_pos, "<", end_pos): break

            char = self.text_area.get(current_pos)
            if char == start_char:
                balance += 1
            elif char == match_char:
                balance -= 1
            
            if balance == 0:
                return current_pos

            current_pos = f"{current_pos}{direction:+}c"
        return None

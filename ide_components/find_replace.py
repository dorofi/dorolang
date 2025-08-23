import tkinter as tk
from tkinter import ttk, messagebox

class FindReplaceDialog(tk.Toplevel):
    """Диалоговое окно для поиска и замены"""
    def __init__(self, parent, editor, replace_mode=False):
        super().__init__(parent)
        self.parent = parent
        self.editor = editor
        
        self.title("Найти и Заменить" if replace_mode else "Найти")
        self.transient(parent)
        self.resizable(False, False)
        
        self.protocol("WM_DELETE_WINDOW", self.close_dialog)
        
        self.find_text = tk.StringVar()
        self.replace_text = tk.StringVar()
        self.match_case = tk.BooleanVar()
        self.wrap_around = tk.BooleanVar(value=True)
        
        self.create_widgets(replace_mode)
        self.layout_widgets(replace_mode)
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.find_entry.focus_set()

    def create_widgets(self, replace_mode):
        self.main_frame = ttk.Frame(self, padding="10")
        
        ttk.Label(self.main_frame, text="Найти:").grid(row=0, column=0, sticky="w", pady=2)
        self.find_entry = ttk.Entry(self.main_frame, textvariable=self.find_text, width=40)
        
        if replace_mode:
            ttk.Label(self.main_frame, text="Заменить на:").grid(row=1, column=0, sticky="w", pady=2)
            self.replace_entry = ttk.Entry(self.main_frame, textvariable=self.replace_text, width=40)
        
        self.options_frame = ttk.Frame(self.main_frame)
        self.case_check = ttk.Checkbutton(self.options_frame, text="Учитывать регистр", variable=self.match_case)
        self.wrap_check = ttk.Checkbutton(self.options_frame, text="Искать с начала", variable=self.wrap_around)
        
        self.button_frame = ttk.Frame(self)
        self.find_button = ttk.Button(self.button_frame, text="Найти далее", command=self.find_next)
        self.cancel_button = ttk.Button(self.button_frame, text="Отмена", command=self.close_dialog)
        
        if replace_mode:
            self.replace_button = ttk.Button(self.button_frame, text="Заменить", command=self.replace)
            self.replace_all_button = ttk.Button(self.button_frame, text="Заменить все", command=self.replace_all)

    def layout_widgets(self, replace_mode):
        self.main_frame.pack(fill="both", expand=True)
        
        self.find_entry.grid(row=0, column=1, sticky="ew", pady=2)
        if replace_mode:
            self.replace_entry.grid(row=1, column=1, sticky="ew", pady=2)
        
        self.options_frame.grid(row=2, column=1, sticky="w", pady=5)
        self.case_check.pack(side="left")
        self.wrap_check.pack(side="left", padx=10)
        
        self.button_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.cancel_button.pack(side="right", padx=2)
        self.find_button.pack(side="right", padx=2)
        if replace_mode:
            self.replace_all_button.pack(side="right", padx=2)
            self.replace_button.pack(side="right", padx=2)

    def find_next(self):
        text_widget = self.editor.text_area
        query = self.find_text.get()
        if not query: return
            
        start_pos = text_widget.index(tk.INSERT)
        pos = text_widget.search(query, start_pos, stopindex=tk.END, nocase=not self.match_case.get())
        
        if not pos and self.wrap_around.get():
            if messagebox.askyesno("Поиск", "Достигнут конец файла. Продолжить с начала?", parent=self):
                pos = text_widget.search(query, "1.0", stopindex=start_pos, nocase=not self.match_case.get())
        
        if pos:
            end_pos = f"{pos}+{len(query)}c"
            text_widget.tag_remove(tk.SEL, "1.0", tk.END)
            text_widget.tag_add(tk.SEL, pos, end_pos)
            text_widget.mark_set(tk.INSERT, end_pos)
            text_widget.see(pos)
            self.lift()
        else:
            messagebox.showinfo("Поиск", f"Не удалось найти '{query}'", parent=self)

    def replace(self):
        text_widget = self.editor.text_area
        query = self.find_text.get()
        replacement = self.replace_text.get()
        if not query: return
            
        try:
            sel_start = text_widget.index(tk.SEL_FIRST)
            sel_end = text_widget.index(tk.SEL_LAST)
            selected_text = text_widget.get(sel_start, sel_end)
            
            if (self.match_case.get() and selected_text == query) or \
               (not self.match_case.get() and selected_text.lower() == query.lower()):
                text_widget.delete(sel_start, sel_end)
                text_widget.insert(sel_start, replacement)
            self.find_next()
        except tk.TclError:
            self.find_next()

    def replace_all(self):
        text_widget = self.editor.text_area
        query = self.find_text.get()
        replacement = self.replace_text.get()
        if not query: return
            
        count = 0
        start_pos = "1.0"
        while True:
            pos = text_widget.search(query, start_pos, stopindex=tk.END, nocase=not self.match_case.get())
            if not pos: break
            
            end_pos = f"{pos}+{len(query)}c"
            text_widget.delete(pos, end_pos)
            text_widget.insert(pos, replacement)
            start_pos = f"{pos}+{len(replacement)}c"
            count += 1
            
        messagebox.showinfo("Заменить все", f"Выполнено замен: {count}", parent=self)
        self.close_dialog()

    def close_dialog(self):
        self.parent.find_window = None
        self.destroy()

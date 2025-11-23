import tkinter as tk
from tkinter import ttk, scrolledtext
import re
import traceback
from ide_settings import THEMES

class Console:
    """Enhanced console for output results"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.setup_console()
    
    def setup_console(self):
        """Setup console"""
        try:
            self.colors = THEMES['light'] # Temporary value until theme is applied

            self.header_frame = ttk.Frame(self.frame)
            self.header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
            
            self.console_label = ttk.Label(self.header_frame, text="🖥️ Console Output", font=("Arial", 10, "bold"))
            self.console_label.pack(side=tk.LEFT)
            
            clear_button = ttk.Button(self.header_frame, text="🧹 Clear", command=self.clear)
            clear_button.pack(side=tk.RIGHT)
            
            self.console_text = scrolledtext.ScrolledText(
                self.frame,
                height=12,
                wrap=tk.WORD,
                font=("Consolas", 10),
                state=tk.DISABLED
            )
            self.console_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
        except Exception as e:
            print(f"Ошибка настройки консоли: {e}")
            traceback.print_exc()
            raise

    def apply_theme(self, colors):
        """Applies new color scheme to console"""
        self.colors = colors
        self.console_text.config(
            background=colors['console_bg'],
            foreground=colors['console_fg'],
            insertbackground=colors['insert_bg']
        )
        self.console_text.tag_config("output", foreground=colors['console_output'])
        self.console_text.tag_config("error", foreground=colors['console_error'])
        self.console_text.tag_config("info", foreground=colors['console_info'])
        self.console_text.tag_config("warning", foreground=colors['console_warning'])
        self.console_text.tag_config("success", foreground=colors['console_success'])
        self.console_text.tag_config("boolean", foreground=colors['console_boolean'])
        self.console_text.tag_config("number", foreground=colors['console_number'])
    
    def write(self, text, tag="output"):
        """Write text to console with enhanced formatting"""
        try:
            self.console_text.config(state=tk.NORMAL)
            
            if "true" in text.lower() or "false" in text.lower():
                if tag == "output":
                    tag = "boolean"
            elif re.search(r'\d+', text):
                if tag == "output" and not any(char.isalpha() for char in text if char not in "0123456789. "):
                    tag = "number"
            
            self.console_text.insert(tk.END, text, tag)
            self.console_text.see(tk.END)
            self.console_text.config(state=tk.DISABLED)
            self.console_text.update()
        except Exception as e:
            print(f"Error writing to console: {e}")
    
    def clear(self):
        """Clear console"""
        try:
            self.console_text.config(state=tk.NORMAL)
            self.console_text.delete("1.0", tk.END)
            self.console_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Ошибка очистки консоли: {e}")
    
    def write_info(self, text): self.write(f"ℹ️ {text}\n", "info")
    def write_error(self, text): self.write(f"❌ {text}\n", "error")
    def write_warning(self, text): self.write(f"⚠️ {text}\n", "warning")
    def write_success(self, text): self.write(f"✅ {text}\n", "success")


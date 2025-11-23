<p align="center">
  <img src="doroff_logo.svg" alt="DoroLang Logo" width="160"/>
</p>

# DoroLang — Educational Programming Language with IDE

> **DoroLang** is a modern, simple, and intuitive interpreted programming language with its own cross-platform IDE. The project is created for learning programming from scratch, experimentation, and creativity.

---

## 🚀 Key Features

### DoroLang Language
- Simple syntax, similar to Python and pseudocode
- Variables (`kas`), strings, numbers, boolean values (`true`/`false`)
- Arithmetic (`+`, `-`, `*`, `/`, `%`), comparisons (`==`, `!=`, `<`, `>`, `<=`, `>=`)
- Logic (`and`, `or`, `not`), conditional constructs `if-else`
- **Loops:** `while` and `for` loops with step support
- **Functions:** Define and call functions with parameters and return values
- **Complete HTML Tutorial:** Interactive tutorial with examples (index.html)
- Comments (`#`)
- Automatic type coercion during concatenation
- `input()` function for interactive data input

### DoroLang IDE
- **Syntax highlighting** with support for keywords, strings, numbers, booleans, and logical operators
- **Line numbering** with synchronized scrolling
- **Built-in console** with color-coded output (info, error, warning, success)
- **File explorer** with create, rename, delete operations
- **Multi-file editing** with tabbed interface
- **Code templates** for quick start (8+ templates included)
- **Find & Replace** functionality
- **Enhanced autocomplete** (Ctrl+Space) with keywords and variable suggestions
- **Go to Line** (Ctrl+G)
- **Comment/Uncomment** (Ctrl+/)
- **Syntax checking** without execution with error highlighting
- **Error highlighting** - shows line numbers and highlights error lines in red
- **Settings window** with theme and editor preferences
- **Recent files** support in File menu
- **Light and Dark themes**
- **Quick run** (F5), **Run selection** (F9), save (Ctrl+S)
- **Auto-save** before running
- **Interactive input** support via dialog boxes
- **Close tab** (Ctrl+W) and **Close all tabs** options
- Work with `.doro` files
- Cross-platform (Python + Tkinter)

---

## 🛠️ Installation and Running

### Requirements
- Python 3.6+

### Running the IDE
```zsh
python dorolang_ide.py
```

### Command Line Usage
- **REPL:**
  ```zsh
  python main.py interactive
  ```
- **Run file:**
  ```zsh
  python main.py my_program.doro
  ```

---

## 📚 Quick Start: Syntax

### Variables and Output
```doro
kas name = input("What is your name?")
say "Hello, " + name
```

### Conditionals
```doro
kas age = input("How old are you?")
if (age >= 18) {
  say "Access granted."
} else {
  say "Access denied."
}
```

### Example Program
```doro
# Mini questionnaire
kas user = input("Enter name:")
say "Welcome, " + user
kas ready = input("Ready to start? (yes/no):")
if (ready == "yes") {
  say "Let's go!"
} else {
  say "See you later!"
}
```

---

## 🆕 Changelog
- **Latest (v1.4):** Major language features:
  - ✅ **While loops** - repeat code while condition is true
  - ✅ **For loops** - iterate with start, end, and optional step
  - ✅ **Functions** - define and call functions with parameters
  - ✅ **Return statements** - return values from functions
  - ✅ **HTML Tutorial** - complete interactive tutorial (index.html)
- **v1.3:** Major IDE improvements:
  - ✅ Full English translation of codebase and documentation
  - ✅ Settings window with theme and editor preferences
  - ✅ Error highlighting - shows line numbers and highlights error lines
  - ✅ Enhanced autocomplete with variable suggestions
  - ✅ Recent files support in File menu
  - ✅ More code templates (Input Example, Nested Conditionals, Logical Operators, String Operations)
  - ✅ Improved error messages with line and column numbers
  - ✅ File explorer with file/folder management
  - ✅ Code templates system
  - ✅ Find & Replace dialog
  - ✅ Improved syntax highlighting
  - ✅ Theme support (Light/Dark)
- **23.11.2025:** Added `input()` function for interactive input
- Improved documentation and examples

---

## ⌨️ IDE Keyboard Shortcuts

### Files
- `Ctrl+N` - New file
- `Ctrl+T` - New from template
- `Ctrl+O` - Open file
- `Ctrl+S` - Save
- `Ctrl+Shift+S` - Save as

### Editing
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+X` - Cut
- `Ctrl+C` - Copy
- `Ctrl+V` - Paste
- `Ctrl+A` - Select all
- `Ctrl+/` - Toggle comment
- `Ctrl+Space` - Autocomplete
- `Ctrl+F` - Find
- `Ctrl+H` - Replace
- `Ctrl+G` - Go to line

### Tabs
- `Ctrl+W` - Close current tab

### Execution
- `F5` - Run code
- `F9` - Run selection

## ❓ FAQ
- **Q:** How to add custom functions?
  **A:** Study the `parser.py` and `interpreter.py` files — the architecture is open for extension.
- **Q:** Can it run on Windows/Mac?
  **A:** Yes, only Python 3.6+ is required.
- **Q:** What if DoroLang modules are not found?
  **A:** The IDE will run in demo mode. Place `lexer.py`, `parser.py`, and `interpreter.py` in the same folder for full functionality.

---

## 👨‍💻 Author
- Dorofii Karnaukh

---

<p align="center"><sub>Project for learning and inspiration. Welcome to the world of programming!</sub></p>

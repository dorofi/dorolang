import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
import shutil

class FileExplorer:
    """Панель проводника файлов проекта"""
    def __init__(self, parent, ide_instance, doro_icon=None):
        self.parent = parent
        self.ide = ide_instance
        self.doro_icon = doro_icon
        self.frame = ttk.Frame(parent, style="Explorer.TFrame")
        
        self.tree = ttk.Treeview(self.frame, show='tree')
        self.vsb = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.on_double_click)
        
        self.path_map = {}
        self.root_path = None
        self.selected_item_id = None

        self.create_context_menu()

    def populate_tree(self, path):
        """Заполняет дерево файлами и папками из указанного пути"""
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.path_map.clear()
        
        self.root_path = path
        root_node = self.tree.insert("", 'end', text=f"🗂️ {os.path.basename(path)}", open=True)
        self.path_map[root_node] = path
        self.process_directory(root_node, path)

    def process_directory(self, parent_id, path):
        """Рекурсивно обрабатывает директорию"""
        try:
            for p in sorted(os.listdir(path)):
                abs_path = os.path.join(path, p)
                is_dir = os.path.isdir(abs_path)

                if is_dir:
                    node_text = f"📁 {p}"
                    node_image = ""  # У папок нет иконки
                else:
                    node_text = f"📄 {p}"
                    node_image = ""  # Иконка по умолчанию для файлов
                    if p.endswith('.doro') and self.doro_icon:
                        node_text = f" {p}"  # Пробел для отступа от иконки
                        node_image = self.doro_icon

                node_id = self.tree.insert(parent_id, 'end', text=node_text, image=node_image, open=False)

                self.path_map[node_id] = abs_path
                
                if is_dir:
                    self.process_directory(node_id, abs_path)
        except PermissionError:
            self.tree.insert(parent_id, 'end', text="🚫 Доступ запрещен")
        except Exception as e:
            print(f"Ошибка обработки директории {path}: {e}")

    def on_double_click(self, event):
        """Обработчик двойного клика для открытия файла"""
        try:
            item_id = self.tree.identify_row(event.y)
            if item_id:
                path = self.path_map.get(item_id)
                if path and os.path.isfile(path):
                    self.ide.open_file_from_path(path)
        except Exception as e:
            print(f"Ошибка открытия файла из проводника: {e}")

    def create_context_menu(self):
        """Создает контекстное меню для дерева файлов"""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Новый файл...", command=self.new_file)
        self.context_menu.add_command(label="Новая папка...", command=self.new_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Переименовать...", command=self.rename_item)
        self.context_menu.add_command(label="Удалить", command=self.delete_item)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Обновить", command=self.refresh_tree)
        
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Показывает контекстное меню при правом клике"""
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            self.selected_item_id = item_id
            is_root = self.tree.parent(item_id) == ""
            self.context_menu.entryconfig("Переименовать...", state="disabled" if is_root else "normal")
            self.context_menu.entryconfig("Удалить", state="disabled" if is_root else "normal")
            self.context_menu.post(event.x_root, event.y_root)

    def get_selected_path(self):
        """Получает путь к папке, в которой нужно создать новый элемент"""
        if not self.selected_item_id: return self.root_path
        path = self.path_map.get(self.selected_item_id)
        return path if os.path.isdir(path) else os.path.dirname(path)

    def new_file(self):
        target_dir = self.get_selected_path()
        if not target_dir: return
        file_name = simpledialog.askstring("Новый файл", "Введите имя файла:", parent=self.ide)
        if file_name:
            try:
                new_path = os.path.join(target_dir, file_name)
                if not os.path.exists(new_path):
                    with open(new_path, 'w', encoding='utf-8') as f: pass
                    self.refresh_tree()
                    self.ide.open_file_from_path(new_path)
                else: messagebox.showwarning("Ошибка", "Файл с таким именем уже существует.", parent=self.ide)
            except Exception as e: messagebox.showerror("Ошибка", f"Не удалось создать файл: {e}", parent=self.ide)

    def new_folder(self):
        target_dir = self.get_selected_path()
        if not target_dir: return
        folder_name = simpledialog.askstring("Новая папка", "Введите имя папки:", parent=self.ide)
        if folder_name:
            try:
                os.makedirs(os.path.join(target_dir, folder_name), exist_ok=False)
                self.refresh_tree()
            except FileExistsError: messagebox.showwarning("Ошибка", "Папка с таким именем уже существует.", parent=self.ide)
            except Exception as e: messagebox.showerror("Ошибка", f"Не удалось создать папку: {e}", parent=self.ide)

    def delete_item(self):
        path_to_delete = self.path_map.get(self.selected_item_id)
        if not path_to_delete: return
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить '{os.path.basename(path_to_delete)}'?", parent=self.ide):
            try:
                if os.path.isfile(path_to_delete): os.remove(path_to_delete)
                elif os.path.isdir(path_to_delete): shutil.rmtree(path_to_delete)
                self.refresh_tree()
            except Exception as e: messagebox.showerror("Ошибка", f"Не удалось удалить: {e}", parent=self.ide)

    def rename_item(self):
        old_path = self.path_map.get(self.selected_item_id)
        if not old_path: return
        old_name = os.path.basename(old_path)
        new_name = simpledialog.askstring("Переименовать", "Введите новое имя:", initialvalue=old_name, parent=self.ide)
        if new_name and new_name != old_name:
            try:
                os.rename(old_path, os.path.join(os.path.dirname(old_path), new_name))
                self.refresh_tree()
            except Exception as e: messagebox.showerror("Ошибка", f"Не удалось переименовать: {e}", parent=self.ide)

    def refresh_tree(self):
        if self.root_path and os.path.isdir(self.root_path):
            self.populate_tree(self.root_path)

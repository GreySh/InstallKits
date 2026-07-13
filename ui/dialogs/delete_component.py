"""
Диалог удаления компонента (носитель/коробка).
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from data import get_all_discs, get_all_boxes, delete_disc, delete_box
from ui.dialogs.base_dialog import BaseDialog


class DeleteComponentDialog(BaseDialog):
    def get_default_geometry(self):
        return "300x300"
    
    def __init__(self, master, stock_tab=None):
        super().__init__(master)
        
        self.title("Удалить компонент")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.accepted = False
        self.stock_tab = stock_tab
        
        # Заголовок
        ctk.CTkLabel(self, text="Выберите компонент для удаления:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Treeview для выбора компонента
        self.components_tree = ttk.Treeview(self, columns=("name",), show="tree headings")
        self.components_tree.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.components_tree.heading("#0", text="Тип")
        self.components_tree.heading("name", text="Название")
        self.components_tree.column("#0", width=80, anchor="w")
        self.components_tree.column("name", width=150, anchor="w")
        
        # Список компонентов
        self.components_list = []
        
        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        
        self.cancel_button = ctk.CTkButton(button_frame, text="Отмена", command=self.cancel)
        self.cancel_button.pack(side="right", padx=5)
        
        self.delete_button = ctk.CTkButton(button_frame, text="Удалить", command=self.delete, fg_color="red")
        self.delete_button.pack(side="right", padx=5)
        
        # Загрузить компоненты
        self.load_components()
        
        # Привязать двойной клик для удаления
        self.components_tree.bind("<Double-1>", self.on_double_click)
    
    def load_components(self):
        """Загрузить список компонентов."""
        # Очистить дерево
        for item in self.components_tree.get_children():
            self.components_tree.delete(item)
        
        self.components_list = []
        
        # Загрузить носители
        discs = get_all_discs()
        for disc in discs:
            item_id = self.components_tree.insert("", "end", text="Носитель", values=(disc['name'],))
            self.components_list.append({"id": disc.doc_id, "name": disc['name'], "type": "Носитель", "item_id": item_id})
        
        # Загрузить коробки
        boxes = get_all_boxes()
        for box in boxes:
            item_id = self.components_tree.insert("", "end", text="Коробка", values=(box['name'],))
            self.components_list.append({"id": box.doc_id, "name": box['name'], "type": "Коробка", "item_id": item_id})
    
    def on_double_click(self, event):
        """Удалить по двойному клику."""
        selected = self.components_tree.selection()
        if selected:
            self.selected_item = self.components_tree.item(selected[0])
            self.delete()
    
    def delete(self):
        """Удалить выбранный компонент."""
        selected = self.components_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите компонент для удаления")
            return
        
        item = self.components_tree.item(selected[0])
        component_name = item['values'][0]
        component_type = item['text']
        
        # Найти компонент в списке
        component = None
        for comp in self.components_list:
            if comp['name'] == component_name and comp['type'] == component_type:
                component = comp
                break
        
        if not component:
            messagebox.showerror("Ошибка", "Не удалось найти компонент")
            return
        
        # Подтверждение удаления
        confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить {component_type.lower()} \"{component_name}\"?")
        
        if confirm:
            try:
                if component_type == "Носитель":
                    delete_disc(component['id'])
                else:
                    delete_box(component['id'])
                
                self.accepted = True
                self.destroy()
                
                # Обновить вкладки
                if self.stock_tab:
                    self.stock_tab.load_stock()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить компонент: {str(e)}")
    
    def cancel(self):
        """Обработать нажатие кнопки Cancel."""
        self.accepted = False
        self.destroy()

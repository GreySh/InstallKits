"""
Вкладка управления остатками.
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from data import get_all_discs, get_all_boxes, delete_disc, delete_box
from ui.dialogs.add_all import AddAllDialog
from ui.dialogs.adjust_stock import AdjustStockDialog
from ui.dialogs.add_stock import AddStockDialog
from ui.dialogs.add_component import AddComponentDialog


class StockTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Заголовок
        self.title_label = ctk.CTkLabel(self, text="Управление остатками", font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="w")
        
        # Кнопки добавления и редактирования
        button_frame_top = ctk.CTkFrame(self)
        button_frame_top.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        
        self.add_all_button = ctk.CTkButton(button_frame_top, text="Добавить", command=self.add_all)
        self.add_all_button.pack(side="left", padx=5)
        
        self.edit_button = ctk.CTkButton(button_frame_top, text="Редактировать", command=self.edit_stock)
        self.edit_button.pack(side="right", padx=5)
        
        # Таблица остатков
        self.stock_tree = ttk.Treeview(self, columns=("name", "quantity"), show="tree headings")
        self.stock_tree.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        
        # Заголовки колонок
        self.stock_tree.heading("#0", text="Тип", command=lambda: self.sort_by("type"))
        self.stock_tree.heading("name", text="Название", command=lambda: self.sort_by("name"))
        self.stock_tree.heading("quantity", text="Количество", command=lambda: self.sort_by("quantity"))
        
        # Настройка ширин колонок
        self.stock_tree.column("#0", width=10, anchor="center")
        self.stock_tree.column("name", width=200, anchor="w")
        self.stock_tree.column("quantity", width=50, anchor="w")
        
        # Кнопки управления компонентами
        button_frame_bottom = ctk.CTkFrame(self)
        button_frame_bottom.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        
        self.add_component_button = ctk.CTkButton(button_frame_bottom, text="Новый компонент", command=self.add_component)
        self.add_component_button.pack(side="left", padx=5)
        
        self.delete_component_button = ctk.CTkButton(button_frame_bottom, text="Удалить компонент", command=self.delete_component, fg_color="red")
        self.delete_component_button.pack(side="right", padx=5)
        
        # Состояние сортировки
        self.sort_column = "type"
        self.sort_reverse = False
        
        # Загрузить остатки
        self.load_stock()
    
    def sort_by(self, column):
        """Сортировка по колонке."""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Получить все элементы
        items = []
        for item_id in self.stock_tree.get_children():
            item = self.stock_tree.item(item_id)
            items.append((item_id, item['text'], item['values']))
        
        # Сортировать
        if column == "type":
            items.sort(key=lambda x: x[1], reverse=self.sort_reverse)
        elif column == "name":
            items.sort(key=lambda x: x[2][0], reverse=self.sort_reverse)
        elif column == "quantity":
            items.sort(key=lambda x: x[2][1], reverse=self.sort_reverse)
        
        # Очистить и пересоздать
        for item_id in self.stock_tree.get_children():
            self.stock_tree.delete(item_id)
        
        for item_id, text, values in items:
            self.stock_tree.insert("", "end", text=text, values=values)
    
    def load_stock(self):
        """Загрузить остатки в таблицу."""
        # Очистить таблицу
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        # Загрузить носители
        from data import get_all_stock_discs
        discs = get_all_stock_discs()
        for disc in discs:
            self.stock_tree.insert("", "end", text="Носитель", values=(disc['disc_name'], disc['quantity']))
        
        # Загрузить коробки
        from data import get_all_stock_boxes
        boxes = get_all_stock_boxes()
        for box in boxes:
            self.stock_tree.insert("", "end", text="Коробка", values=(box['box_name'], box['quantity']))
    
    def load_all(self):
        """Загрузить все данные (для перезагрузки после изменения настроек)."""
        self.load_stock()
    
    def add_component(self):
        """Открыть диалог добавления нового компонента."""
        root = self.winfo_toplevel()
        view_tab = getattr(root, 'view_stock_tab', None)
        dialog = AddComponentDialog(root, self, view_tab)
        if dialog.accepted:
            self.load_stock()
            if view_tab:
                view_tab.load_all()
    
    def edit_stock(self):
        """Открыть диалог редактирования остатка."""
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите компонент для редактирования")
            return
        
        item = self.stock_tree.item(selected[0])
        component_name = item['values'][0]
        component_type = item['text']
        
        # Открыть диалог редактирования с выбранным компонентом
        root = self.winfo_toplevel()
        view_tab = getattr(root, 'view_stock_tab', None)
        
        dialog = AdjustStockDialog(root, self, view_tab, {"name": component_name, "type": component_type})
        if dialog.accepted:
            self.load_stock()
            if view_tab:
                view_tab.load_all()
    
    def delete_component(self):
        """Удалить выбранный компонент."""
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите компонент для удаления")
            return
        
        item = self.stock_tree.item(selected[0])
        component_name = item['values'][0]
        component_type = item['text']
        
        # Подтверждение удаления
        confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить {component_type.lower()} \"{component_name}\"?")
        
        if confirm:
            try:
                # Найти и удалить компонент
                if component_type == "Носитель":
                    from data import get_disc_by_name
                    disc = get_disc_by_name(component_name)
                    if disc:
                        delete_disc(disc.doc_id)
                else:
                    from data import get_box_by_name
                    box = get_box_by_name(component_name)
                    if box:
                        delete_box(box.doc_id)
                
                self.load_stock()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить компонент: {str(e)}")
    
    def add_all(self):
        """Открыть диалог добавления остатков."""
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите компонент для добавления остатков")
            return
        
        item = self.stock_tree.item(selected[0])
        component_name = item['values'][0]
        component_type = item['text']
        
        root = self.winfo_toplevel()
        view_tab = getattr(root, 'view_stock_tab', None)
        dialog = AddStockDialog(root, self, view_tab, {"name": component_name, "type": component_type})
        if dialog.accepted:
            self.load_stock()
            if view_tab:
                view_tab.load_all()
    
    def adjust_stock(self):
        """Открыть диалог корректировки остатков."""
        root = self.winfo_toplevel()
        view_tab = getattr(root, 'view_stock_tab', None)
        dialog = AdjustStockDialog(root, self, view_tab)
        if dialog.accepted:
            self.load_stock()
            if view_tab:
                view_tab.load_all()

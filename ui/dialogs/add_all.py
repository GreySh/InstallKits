"""
Диалог добавления носителей/коробок (существующих видов).
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from data import get_all_discs, get_all_boxes, add_stock_disc, add_stock_box, get_stock_disc_quantity, get_stock_box_quantity
from ui.dialogs.base_dialog import BaseDialog
from ui.spinbox import CTkSpinbox


class AddAllDialog(BaseDialog):
    def get_default_geometry(self):
        return "400x400"
    
    def __init__(self, master, stock_tab=None, selected_item=None):
        super().__init__(master)
        
        self.title("Добавить носители/коробки")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.accepted = False
        self.type_index = 0  # 0 = disc, 1 = box
        self.stock_tab = stock_tab
        self.selected_item = selected_item
        
        # Получить корневой виджет (MainWindow) для получения ссылок на вкладки
        try:
            root = master.winfo_toplevel()
            # Использовать переданные параметры, если они есть, иначе получить из главного окна
            if self.stock_tab is None and hasattr(root, 'stock_tab'):
                self.stock_tab = root.stock_tab
        except:
            pass  # Если не удалось получить корневой виджет, использовать переданные параметры
        
        # Тип
        type_frame = ctk.CTkFrame(self)
        type_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(type_frame, text="Тип:").pack(side="left", padx=10)
        
        def on_type_change(value):
            if value == "Коробка":
                self.type_index = 1
            else:
                self.type_index = 0
            self.load_items()
        
        self.type_combobox = ctk.CTkComboBox(type_frame, values=["Носитель", "Коробка"], command=on_type_change)
        self.type_combobox.pack(side="left", padx=10)
        
        # Список
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        list_frame.grid_columnconfigure(1, weight=1)
        
        select_row = ctk.CTkFrame(list_frame)
        select_row.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(select_row, text="Выберите:").pack(side="left", padx=5)
        self.item_combobox = ctk.CTkComboBox(select_row, values=[], state="readonly", command=self._on_item_selected)
        self.item_combobox.pack(side="left", padx=5, fill="x", expand=True)
        self.item_combobox.set("")

        self.current_label = ctk.CTkLabel(list_frame, text="Текущий остаток: 0")
        self.current_label.pack(anchor="w", padx=5, pady=5)
        
        # Приход
        qty_row = ctk.CTkFrame(self)
        qty_row.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(qty_row, text="Приход:").pack(side="left", padx=10)
        self.quantity_entry = CTkSpinbox(qty_row, start=0)
        self.quantity_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        # Разделитель перед кнопками
        separator = ctk.CTkFrame(self, height=2, fg_color=("gray80", "gray30"))
        separator.grid(row=3, column=0, padx=20, pady=(12, 0), sticky="ew")

        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=4, column=0, padx=10, pady=(18, 12), sticky="e")
        
        self.cancel_button = ctk.CTkButton(button_frame, text="Отмена", command=self.cancel)
        self.cancel_button.pack(side="right", padx=5)
        
        self.ok_button = ctk.CTkButton(button_frame, text="Добавить", command=self.ok)
        self.ok_button.pack(side="right", padx=5)
        
        # Инициализация
        if self.selected_item:
            self.type_index = 1 if self.selected_item['type'] == "Коробка" else 0
            self.type_combobox.set(self.selected_item['type'])
            self.load_items()
            self.item_combobox.set(self.selected_item['name'])
            self._on_item_selected(self.selected_item['name'])
        else:
            self.load_items()
    
    def load_items(self):
        """Загрузить список носителей/коробок."""
        if self.type_index == 0:
            items = get_all_discs()
            self.item_combobox.configure(values=[item['name'] for item in items])
        else:
            items = get_all_boxes()
            self.item_combobox.configure(values=[item['name'] for item in items])
    
    def _on_item_selected(self, value):
        """Показать текущий остаток при выборе элемента."""
        name = value.strip() if value else ""
        if not name:
            self.current_label.configure(text="Текущий остаток: 0")
            return

        if self.type_index == 0:
            from data import get_disc_by_name
            item = get_disc_by_name(name)
            if item:
                qty = get_stock_disc_quantity(item.doc_id)
                self.current_label.configure(text=f"Текущий остаток: {qty}")
                return
        else:
            from data import get_box_by_name
            item = get_box_by_name(name)
            if item:
                qty = get_stock_box_quantity(item.doc_id)
                self.current_label.configure(text=f"Текущий остаток: {qty}")
                return

        self.current_label.configure(text="Текущий остаток: 0")

    def ok(self):
        """Обработать нажатие кнопки OK."""
        item_name = self.item_combobox.get().strip()
        quantity = self.quantity_entry.get().strip()
        
        if not item_name:
            messagebox.showerror("Ошибка", "Выберите носитель/коробку")
            return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
            return
        
        if self.type_index == 0:
            from data import get_disc_by_name
            item = get_disc_by_name(item_name)
            if item:
                add_stock_disc(item.doc_id, quantity)
        else:
            from data import get_box_by_name
            item = get_box_by_name(item_name)
            if item:
                add_stock_box(item.doc_id, quantity)
        
        self.accepted = True
        self.destroy()
        
        # Обновить вкладки
        if self.stock_tab:
            self.stock_tab.load_stock()
        if self.stock_tab:
            self.stock_tab.load_all()
        main_window = self.master
        if hasattr(main_window, 'tabs'):
            if "Состав ИК" in main_window.tabs:
                main_window.tabs["Состав ИК"].load_all()
            if "Списание" in main_window.tabs:
                main_window.tabs["Списание"].load_all()
            if "Операции" in main_window.tabs:
                main_window.tabs["Операции"].load_operations()
    
    def cancel(self):
        """Обработать нажатие кнопки Cancel."""
        self.accepted = False
        self.destroy()

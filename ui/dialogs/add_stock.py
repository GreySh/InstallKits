"""
Диалог добавления остатков.
"""

import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from data import get_all_stock_discs, get_all_stock_boxes, adjust_stock_disc, adjust_stock_box
from ui.dialogs.base_dialog import BaseDialog
from ui.spinbox import CTkSpinbox


class AddStockDialog(BaseDialog):
    def get_default_geometry(self):
        return "400x350"
    
    def __init__(self, master, stock_tab=None, selected_item=None):
        super().__init__(master)
        
        self.title("Добавление остатков")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        
        self.accepted = False
        self.type_index = 0  # 0 = disc, 1 = box
        self.stock_tab = stock_tab
        self.selected_item = selected_item  # Выбранный компонент из таблицы
        
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
        list_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(list_frame, text="Выберите:").pack(anchor="w", padx=5, pady=5)
        
        self.item_combobox = ttk.Combobox(list_frame, values=[], state="readonly", height=10)
        self.item_combobox.pack(fill="x", padx=5, pady=5)
        
        self.item_combobox.bind("<<ComboboxSelected>>", self._on_item_selected)
        
        # Текущий остаток
        self.current_label = ctk.CTkLabel(list_frame, text="Текущий остаток: 0")
        self.current_label.pack(anchor="w", padx=5, pady=5)
        
        # Количество
        ctk.CTkLabel(self, text="Количество для добавления:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.quantity_entry = CTkSpinbox(self, start=0)
        self.quantity_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        
        self.cancel_button = ctk.CTkButton(button_frame, text="Отмена", command=self.cancel)
        self.cancel_button.pack(side="right", padx=5)
        
        self.ok_button = ctk.CTkButton(button_frame, text="Добавить", command=self.ok)
        self.ok_button.pack(side="right", padx=5)
        
        # Инициализация
        if self.selected_item:
            # Установить тип и компонент из выбранного
            self.type_index = 1 if self.selected_item['type'] == "Коробка" else 0
            self.type_combobox.set(self.selected_item['type'])
            self.load_items()
            self.item_combobox.set(self.selected_item['name'])
            self.on_item_change(self.selected_item['name'])
        else:
            self.load_items()
    
    def load_items(self):
        """Загрузить список носителей/коробок."""
        if self.type_index == 0:
            items = get_all_stock_discs()
            self.item_combobox.configure(values=[item['disc_name'] for item in items])
        else:
            items = get_all_stock_boxes()
            self.item_combobox.configure(values=[item['box_name'] for item in items])
        
        if self.item_combobox.get() not in self.item_combobox['values']:
            self.item_combobox.set("")
            self.current_label.configure(text="Текущий остаток: 0")
    
    def _on_item_selected(self, e):
        """Обработчик события выбора элемента."""
        selected = self.item_combobox.get()
        self.on_item_change(selected)
    
    def on_item_change(self, value):
        """Обработать изменение выбранного элемента."""
        if self.type_index == 0:
            from data import get_disc_by_name
            item = get_disc_by_name(value)
            if item:
                from data import get_stock_disc_quantity
                qty = get_stock_disc_quantity(item.doc_id)
                self.current_label.configure(text=f"Текущий остаток: {qty}")
                self.quantity_entry.delete(0, 'end')
                # Для добавления предлагаем ввести количество, которое нужно добавить
                self.quantity_entry.insert(0, "1")
            else:
                self.current_label.configure(text="Текущий остаток: 0")
                self.quantity_entry.delete(0, 'end')
        else:
            from data import get_box_by_name
            item = get_box_by_name(value)
            if item:
                from data import get_stock_box_quantity
                qty = get_stock_box_quantity(item.doc_id)
                self.current_label.configure(text=f"Текущий остаток: {qty}")
                self.quantity_entry.delete(0, 'end')
                self.quantity_entry.insert(0, "1")
            else:
                self.current_label.configure(text="Текущий остаток: 0")
                self.quantity_entry.delete(0, 'end')
    
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
        
        # Добавить к текущему остатку
        if self.type_index == 0:
            from data import get_disc_by_name
            item = get_disc_by_name(item_name)
            if item:
                # Получить текущий остаток и добавить к нему
                from data import get_stock_disc_quantity
                current_qty = get_stock_disc_quantity(item.doc_id)
                adjust_stock_disc(item.doc_id, current_qty + quantity)
        else:
            from data import get_box_by_name
            item = get_box_by_name(item_name)
            if item:
                from data import get_stock_box_quantity
                current_qty = get_stock_box_quantity(item.doc_id)
                adjust_stock_box(item.doc_id, current_qty + quantity)
        
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

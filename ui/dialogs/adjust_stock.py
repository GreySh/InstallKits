"""
Диалог корректировки остатков.
"""

import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from data import get_all_stock_discs, get_all_stock_boxes, adjust_stock_disc, adjust_stock_box


class AdjustStockDialog(tk.Toplevel):
    def __init__(self, master, stock_tab=None, view_tab=None):
        super().__init__(master)
        
        self.title("Корректировка остатков")
        self.geometry("400x400")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        self.accepted = False
        self.type_index = 0  # 0 = disc, 1 = box
        self.stock_tab = stock_tab  # Ссылка на вкладку остатков для обновления
        self.view_tab = view_tab    # Ссылка на вкладку просмотра для обновления
        
        # Получить корневой виджет (MainWindow) для получения ссылок на вкладки
        try:
            root = master.nametowidget('.')
            # Использовать переданные параметры, если они есть, иначе получить из главного окна
            if self.stock_tab is None and hasattr(root, 'stock_tab'):
                self.stock_tab = root.stock_tab
            if self.view_tab is None and hasattr(root, 'view_stock_tab'):
                self.view_tab = root.view_stock_tab
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
        
        self.type_combobox = ctk.CTkComboBox(type_frame, values=["Диск", "Коробка"], command=on_type_change)
        self.type_combobox.pack(side="left", padx=10)
        
        # Список
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(list_frame, text="Выберите:").pack(anchor="w", padx=5, pady=5)
        
        # Используем ttk.Combobox вместо CTkComboBox для корректной работы события <<ComboboxSelected>>
        self.item_combobox = ttk.Combobox(list_frame, values=[], state="readonly", height=10)
        self.item_combobox.pack(fill="x", padx=5, pady=5)
        self.item_combobox.set("")  # Установить пустое значение по умолчанию
        
        # Привязать событие выбора элемента
        self.item_combobox.bind("<<ComboboxSelected>>", self._on_item_selected)
        
        # Текущий остаток
        self.current_label = ctk.CTkLabel(list_frame, text="Текущий остаток: 0")
        self.current_label.pack(anchor="w", padx=5, pady=5)
        
        # Количество
        ctk.CTkLabel(self, text="Новое количество:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.quantity_entry = ctk.CTkEntry(self)
        self.quantity_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        
        self.cancel_button = ctk.CTkButton(button_frame, text="Отмена", command=self.cancel)
        self.cancel_button.pack(side="right", padx=5)
        
        self.ok_button = ctk.CTkButton(button_frame, text="Применить", command=self.ok)
        self.ok_button.pack(side="right", padx=5)
        
        # Инициализация
        self.load_items()
        
        # Центрирование
        self.transient(master)
        self.grab_set()
        self.wait_window()
    
    def load_items(self):
        """Загрузить список дисков/коробок."""
        if self.type_index == 0:
            items = get_all_stock_discs()
            self.item_combobox.configure(values=[item['disc_name'] for item in items])
        else:
            items = get_all_stock_boxes()
            self.item_combobox.configure(values=[item['box_name'] for item in items])
        # Очистить текущее значение после изменения списка
        self.item_combobox.set("")
        self.current_label.configure(text="Текущий остаток: 0")
    
    def _on_item_selected(self, e):
        """Обработчик события выбора элемента."""
        selected = self.item_combobox.get()
        self.on_item_change(selected)
    
    def on_item_change(self, value):
        """Обработать изменение выбранного элемента."""
        # Получить текущий остаток
        if self.type_index == 0:
            from data import get_disc_by_name
            item = get_disc_by_name(value)
            if item:
                from data import get_stock_disc_quantity
                qty = get_stock_disc_quantity(item.doc_id)
                self.current_label.configure(text=f"Текущий остаток: {qty}")
            else:
                self.current_label.configure(text="Текущий остаток: 0")
        else:
            from data import get_box_by_name
            item = get_box_by_name(value)
            if item:
                from data import get_stock_box_quantity
                qty = get_stock_box_quantity(item.doc_id)
                self.current_label.configure(text=f"Текущий остаток: {qty}")
            else:
                self.current_label.configure(text="Текущий остаток: 0")
    
    def ok(self):
        """Обработать нажатие кнопки OK."""
        item_name = self.item_combobox.get().strip()
        quantity = self.quantity_entry.get().strip()
        
        if not item_name:
            messagebox.showerror("Ошибка", "Выберите диск/коробку")
            return
        
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть неотрицательным числом")
            return
        
        # Применить изменения
        if self.type_index == 0:
            from data import get_disc_by_name
            item = get_disc_by_name(item_name)
            if item:
                adjust_stock_disc(item.doc_id, quantity)
        else:
            from data import get_box_by_name
            item = get_box_by_name(item_name)
            if item:
                adjust_stock_box(item.doc_id, quantity)
        
        self.accepted = True
        self.destroy()
        
        # Обновить вкладки
        if self.stock_tab:
            self.stock_tab.load_stock()
        if self.view_tab:
            self.view_tab.load_all()
    
    def cancel(self):
        """Обработать нажатие кнопки Cancel."""
        self.accepted = False
        self.destroy()

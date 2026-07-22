"""
Диалог списания комплекта.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from data import (
    get_all_products, get_product_available_quantity, dispatch_product
)
from ui.dialogs.base_dialog import BaseDialog
from ui.spinbox import CTkSpinbox
from ui.widgets.date_picker import DatePicker


class DispatchDialog(BaseDialog):
    def get_default_geometry(self):
        return "400x350"
    
    def __init__(self, master, stock_tab=None):
        super().__init__(master)
        
        self.title("Списать ИК")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        
        self.accepted = False
        self.stock_tab = stock_tab  # Ссылка на вкладку остатков для обновления
        
        # Получить корневой виджет (MainWindow) для получения ссылок на вкладки
        try:
            root = master.nametowidget('.')
            # Использовать переданные параметры, если они есть, иначе получить из главного окна
            if self.stock_tab is None and hasattr(root, 'stock_tab'):
                self.stock_tab = root.stock_tab
        except:
            pass  # Если не удалось получить корневой виджет, использовать переданные параметры
        
        # Дата отгрузки
        ctk.CTkLabel(self, text="Дата отгрузки:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.date_picker = DatePicker(self)
        self.date_picker.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        today = datetime.now().strftime('%d.%m.%Y')
        self.date_picker.insert(0, today)
        
        # Продукт
        ctk.CTkLabel(self, text="Продукт:", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        product_frame = ctk.CTkFrame(self)
        product_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        products = get_all_products()
        product_names = [p['name'] for p in products]
        
        self.product_var = ctk.StringVar(value=product_names[0] if product_names else "")
        self.product_combo = ctk.CTkComboBox(product_frame, values=product_names, variable=self.product_var, command=self.on_product_change)
        self.product_combo.pack(side="left", padx=5)
        
        # Количество
        ctk.CTkLabel(self, text="Количество:", font=("Arial", 12, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.quantity_entry = CTkSpinbox(self, start=1)
        self.quantity_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # Информация о доступном
        self.available_label = ctk.CTkLabel(self, text="Доступно: 0 комплектов", text_color="gray")
        self.available_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="e")
        
        self.cancel_button = ctk.CTkButton(button_frame, text="Отмена", command=self.cancel)
        self.cancel_button.pack(side="right", padx=5)
        
        self.ok_button = ctk.CTkButton(button_frame, text="Списать", command=self.ok)
        self.ok_button.pack(side="right", padx=5)
        
        # Загрузить первую продукцию
        if product_names:
            self.on_product_change(product_names[0])
    
    def on_product_change(self, value):
        """Обработать изменение продукта."""
        products = get_all_products()
        product_id = None
        for p in products:
            if p['name'] == value:
                product_id = p.doc_id
                break

        if product_id:
            min_quantity = get_product_available_quantity(product_id)
            self.available_label.configure(text=f"Доступно: {min_quantity} комплектов")
    
    def ok(self):
        """Обработать нажатие кнопки OK."""
        product_name = self.product_combo.get().strip()
        quantity = self.quantity_entry.get().strip()
        date = self.date_picker.get().strip()

        if not product_name:
            messagebox.showerror("Ошибка", "Выберите продукт")
            return

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
            return

        products = get_all_products()
        product_id = None
        for p in products:
            if p['name'] == product_name:
                product_id = p.doc_id
                break

        if not product_id:
            messagebox.showerror("Ошибка", "Продукт не найден")
            return

        dispatch_date = None
        if date:
            try:
                dispatch_date = datetime.strptime(date, '%d.%m.%Y').strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте ДД.ММ.ГГГГ")
                return

        success, message = dispatch_product(product_id, quantity, dispatch_date)
        if not success:
            messagebox.showerror("Ошибка", message)
            return

        self.accepted = True
        self.destroy()

        if self.stock_tab:
            self.stock_tab.load_stock()
        if self.stock_tab:
            self.stock_tab.load_all()
    
    def cancel(self):
        """Обработать нажатие кнопки Cancel."""
        self.accepted = False
        self.destroy()

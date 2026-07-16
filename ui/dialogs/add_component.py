"""
Диалог добавления нового компонента (носитель/коробка).
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from data import add_disc, add_box
from ui.dialogs.base_dialog import BaseDialog
from ui.spinbox import CTkSpinbox


class AddComponentDialog(BaseDialog):
    def get_default_geometry(self):
        return "340x400"
    
    def __init__(self, master, stock_tab=None, default_type="Носитель"):
        super().__init__(master)
        
        self.title("Добавить компонент")
        
        self.grid_columnconfigure(0, weight=1)
        
        self.accepted = False
        self.stock_tab = stock_tab
        
        # Тип компонента
        type_row = ctk.CTkFrame(self)
        type_row.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(type_row, text="Тип компонента:").pack(side="left", padx=10)
        self.component_type = tk.StringVar(value=default_type)
        type_combobox = ctk.CTkComboBox(type_row, values=["Носитель", "Коробка"], variable=self.component_type, state="readonly")
        type_combobox.pack(side="left", padx=10)
        
        # Название
        name_row = ctk.CTkFrame(self)
        name_row.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(name_row, text="Название:").pack(side="left", padx=10)
        self.name_entry = ctk.CTkEntry(name_row)
        self.name_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        # Описание
        desc_row = ctk.CTkFrame(self)
        desc_row.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(desc_row, text="Описание:").pack(side="left", padx=10)
        self.description_text = ctk.CTkTextbox(desc_row, height=60)
        self.description_text.pack(side="left", padx=10, fill="x", expand=True)

        # Количество
        qty_row = ctk.CTkFrame(self)
        qty_row.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(qty_row, text="Количество:").pack(side="left", padx=10)
        self.quantity_entry = CTkSpinbox(qty_row, start=0)
        self.quantity_entry.pack(side="left", padx=10, fill="x", expand=True)
        
        # Разделитель перед кнопками
        separator = ctk.CTkFrame(self, height=2, fg_color=("gray80", "gray30"))
        separator.grid(row=4, column=0, padx=20, pady=(12, 0), sticky="ew")

        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=5, column=0, padx=10, pady=(18, 12), sticky="e")
        
        self.cancel_button = ctk.CTkButton(button_frame, text="Отмена", command=self.cancel)
        self.cancel_button.pack(side="right", padx=5)
        
        self.ok_button = ctk.CTkButton(button_frame, text="Добавить", command=self.ok)
        self.ok_button.pack(side="right", padx=5)
        
        # Обновить фокус
        self.name_entry.focus_set()
    
    def ok(self):
        """Обработать нажатие кнопки OK."""
        component_type = self.component_type.get()
        name = self.name_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        
        if not name:
            messagebox.showerror("Ошибка", "Введите название компонента")
            return
        
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть неотрицательным числом")
            return
        
        try:
            description = self.description_text.get("1.0", "end-1c").strip()
            if component_type == "Носитель":
                add_disc(name, quantity, description)
            else:
                add_box(name, quantity, description)
            
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
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def cancel(self):
        """Обработать нажатие кнопки Cancel."""
        self.accepted = False
        self.destroy()

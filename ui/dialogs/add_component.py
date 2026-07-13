"""
Диалог добавления нового компонента (носитель/коробка).
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from data import add_disc, add_box
from ui.dialogs.base_dialog import BaseDialog


class AddComponentDialog(BaseDialog):
    def get_default_geometry(self):
        return "300x220"
    
    def __init__(self, master, stock_tab=None):
        super().__init__(master)
        
        self.title("Добавить компонент")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        
        self.accepted = False
        self.stock_tab = stock_tab
        
        # Тип компонента
        ctk.CTkLabel(self, text="Тип компонента:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.component_type = tk.StringVar(value="nositel")
        type_combobox = ctk.CTkComboBox(self, values=["Носитель", "Коробка"], variable=self.component_type, state="readonly")
        type_combobox.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        type_combobox.set("Носитель")
        
        # Название
        ctk.CTkLabel(self, text="Название:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Количество
        ctk.CTkLabel(self, text="Количество:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.quantity_entry = ctk.CTkEntry(self)
        self.quantity_entry.insert(0, "0")
        self.quantity_entry.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        
        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=6, column=0, padx=10, pady=10, sticky="e")
        
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
            if component_type == "Носитель":
                add_disc(name, quantity)
            else:
                add_box(name, quantity)
            
            self.accepted = True
            self.destroy()
            
            # Обновить вкладки
            if self.stock_tab:
                self.stock_tab.load_stock()
            if self.stock_tab:
                self.stock_tab.load_all()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def cancel(self):
        """Обработать нажатие кнопки Cancel."""
        self.accepted = False
        self.destroy()

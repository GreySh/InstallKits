"""
Диалог редактирования комплекта.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from data import update_product_with_components, get_all_discs, get_all_boxes
from ui.dialogs.base_dialog import BaseDialog
from ui.spinbox import CTkSpinbox


class EditProductDialog(BaseDialog):
    def get_default_geometry(self):
        return "520x560"
    
    def __init__(self, master, product_id):
        super().__init__(master)
        
        self.title("Редактировать продукт")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.product_id = product_id
        self.components = []
        
        # Загрузить продукт
        from data import get_product_by_id, get_product_components
        product = get_product_by_id(product_id)
        self.original_name = product['name']
        original_components = get_product_components(product_id)
        
        # Название продукта
        ctk.CTkLabel(self, text="Название продукта:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.name_entry.insert(0, self.original_name)
        
        # Описание
        ctk.CTkLabel(self, text="Описание:", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nw")
        self.description_text = ctk.CTkTextbox(self, height=60)
        self.description_text.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
        self.description_text.insert("1.0", product.get('description', '') or '')
        
        # Фрейм компонентов
        self.components_frame = ctk.CTkFrame(self)
        self.components_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.components_frame.grid_columnconfigure(0, weight=3)
        self.components_frame.grid_columnconfigure(1, weight=0)
        self.components_frame.grid_columnconfigure(2, weight=3)
        self.components_frame.grid_columnconfigure(3, weight=0)
        self.components_frame.grid_columnconfigure(4, weight=0)
        
        # Заголовки
        ctk.CTkLabel(self.components_frame, text="Носитель").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.components_frame, text="Кол-во").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.components_frame, text="Коробка").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.components_frame, text="Кол-во").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.components_frame, text="").grid(row=0, column=4, padx=5, pady=5)
        
        # Добавить строки компонентов
        if original_components:
            for comp in original_components:
                self.add_component_row(
                    comp['disc_id'],
                    comp['disc_quantity'],
                    comp['box_id'],
                    comp['box_quantity']
                )
        else:
            self.add_component_row()
        
        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.add_row_button = ctk.CTkButton(button_frame, text="+ Добавить компонент", command=self.add_component_row)
        self.add_row_button.pack(side="left", padx=5)
        
        self.cancel_button = ctk.CTkButton(button_frame, text="Отмена", command=self.cancel)
        self.cancel_button.pack(side="right", padx=5)
        
        self.ok_button = ctk.CTkButton(button_frame, text="Сохранить", command=self.ok)
        self.ok_button.pack(side="right", padx=5)
    
    def add_component_row(self, disc_id=None, disc_quantity=0, box_id=None, box_quantity=0):
        """Добавить строку компонента."""
        row = len(self.components) + 1
        
        # Загрузить диски и коробки
        discs = get_all_discs()
        boxes = get_all_boxes()
        
        disc_values = ["(нет)"] + [d['name'] for d in discs]
        box_values = ["(нет)"] + [b['name'] for b in boxes]
        
        # Диск
        disc_var = ctk.StringVar(value="(нет)")
        if disc_id:
            disc = next((d for d in discs if d.doc_id == disc_id), None)
            if disc:
                disc_var.set(disc['name'])
        
        disc_combo = ctk.CTkComboBox(self.components_frame, values=disc_values, variable=disc_var)
        disc_combo.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        
        # Кол-во диска
        qty_entry = CTkSpinbox(self.components_frame, width=50, start=disc_quantity)
        qty_entry.grid(row=row, column=1, padx=5, pady=5, sticky="e")
        
        # Коробка
        box_var = ctk.StringVar(value="(нет)")
        if box_id:
            box = next((b for b in boxes if b.doc_id == box_id), None)
            if box:
                box_var.set(box['name'])
        
        box_combo = ctk.CTkComboBox(self.components_frame, values=box_values, variable=box_var)
        box_combo.grid(row=row, column=2, padx=5, pady=5, sticky="ew")
        
        # Кол-во коробки
        qty_entry2 = CTkSpinbox(self.components_frame, width=50, start=box_quantity)
        qty_entry2.grid(row=row, column=3, padx=5, pady=5, sticky="e")
        
        # Кнопка удаления
        delete_button = ctk.CTkButton(self.components_frame, text="×", width=30, command=lambda: self.remove_component_row(row, delete_button))
        delete_button.grid(row=row, column=4, padx=5, pady=5)
        
        self.components.append({
            'disc_combo': disc_combo,
            'disc_qty': qty_entry,
            'box_combo': box_combo,
            'box_qty': qty_entry2,
            'delete_button': delete_button,
            'row': row
        })
    
    def remove_component_row(self, row, button):
        """Удалить строку компонента."""
        for comp in self.components:
            if comp['row'] == row:
                # Удалить виджеты
                comp['disc_combo'].destroy()
                comp['disc_qty'].destroy()
                comp['box_combo'].destroy()
                comp['box_qty'].destroy()
                comp['delete_button'].destroy()
                
                self.components.remove(comp)
                
                # Обновить номера строк
                for i, c in enumerate(self.components):
                    c['row'] = i + 1
                    c['disc_combo'].grid(row=c['row'], column=0)
                    c['disc_qty'].grid(row=c['row'], column=1)
                    c['box_combo'].grid(row=c['row'], column=2)
                    c['box_qty'].grid(row=c['row'], column=3)
                    c['delete_button'].grid(row=c['row'], column=4)
                break
    
    def ok(self):
        """Обработать нажатие кнопки OK."""
        name = self.name_entry.get().strip()
        
        if not name:
            messagebox.showerror("Ошибка", "Введите название продукта")
            return
        
        # Собрать компоненты
        components = []
        for comp in self.components:
            disc_name = comp['disc_combo'].get()
            disc_qty = comp['disc_qty'].get()
            box_name = comp['box_combo'].get()
            box_qty = comp['box_qty'].get()
            
            disc_id = None
            box_id = None
            
            if disc_name != "(нет)":
                from data import get_disc_by_name
                disc = get_disc_by_name(disc_name)
                if disc:
                    disc_id = disc.doc_id
            
            if box_name != "(нет)":
                from data import get_box_by_name
                box = get_box_by_name(box_name)
                if box:
                    box_id = box.doc_id
            
            try:
                disc_qty = int(disc_qty) if disc_qty else 0
                box_qty = int(box_qty) if box_qty else 0
            except ValueError:
                messagebox.showerror("Ошибка", "Количество должно быть числом")
                return
            
            components.append({
                'disc_id': disc_id,
                'disc_quantity': disc_qty,
                'box_id': box_id,
                'box_quantity': box_qty
            })
        
        # Обновить продукт
        description = self.description_text.get("1.0", "end-1c").strip()
        update_product_with_components(self.product_id, name, '', description, components)
        
        self.accepted = True
        self.destroy()
    
    def cancel(self):
        """Обработать нажатие кнопки Cancel."""
        self.accepted = False
        self.destroy()

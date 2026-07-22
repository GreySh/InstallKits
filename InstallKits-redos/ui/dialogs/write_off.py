"""
Диалог списания по браку.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from data import (
    get_all_stock_discs, get_all_stock_boxes,
    get_disc_by_name, get_box_by_name,
    get_stock_disc_quantity, get_stock_box_quantity,
    write_off_component,
)
from ui.dialogs.base_dialog import BaseDialog
from ui.spinbox import CTkSpinbox


class WriteOffDialog(BaseDialog):
    def get_default_geometry(self):
        return "420x430"

    def __init__(self, master, stock_tab=None, selected_item=None):
        super().__init__(master)

        self.title("Списание по браку")

        self.grid_columnconfigure(0, weight=1)

        self.accepted = False
        self.type_index = 0
        self.stock_tab = stock_tab
        self.selected_item = selected_item

        # Тип
        type_frame = ctk.CTkFrame(self)
        type_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(type_frame, text="Тип:").pack(side="left", padx=10)

        def on_type_change(value):
            self.type_index = 1 if value == "Коробка" else 0
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

        # Количество
        qty_row = ctk.CTkFrame(self)
        qty_row.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(qty_row, text="Количество к списанию:").pack(side="left", padx=10)
        self.quantity_entry = CTkSpinbox(qty_row, start=0)
        self.quantity_entry.pack(side="left", padx=10, fill="x", expand=True)

        # Причина
        reason_row = ctk.CTkFrame(self)
        reason_row.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(reason_row, text="Причина (брак):").pack(side="left", padx=10)
        self.reason_entry = ctk.CTkEntry(reason_row, placeholder_text="Описание причины брака...")
        self.reason_entry.pack(side="left", padx=10, fill="x", expand=True)

        # Разделитель перед кнопками
        separator = ctk.CTkFrame(self, height=2, fg_color=("gray80", "gray30"))
        separator.grid(row=4, column=0, padx=20, pady=(12, 0), sticky="ew")

        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=5, column=0, padx=10, pady=(18, 12), sticky="e")

        ctk.CTkButton(button_frame, text="Отмена", command=self.cancel).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Списать", fg_color="red", command=self.ok).pack(side="right", padx=5)

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
        if self.type_index == 0:
            items = get_all_stock_discs()
            self.item_combobox.configure(values=[item['disc_name'] for item in items])
        else:
            items = get_all_stock_boxes()
            self.item_combobox.configure(values=[item['box_name'] for item in items])

        if self.item_combobox.get() not in self.item_combobox.cget("values"):
            self.item_combobox.set("")
            self.current_label.configure(text="Текущий остаток: 0")

    def _on_item_selected(self, value=None):
        self._on_item_change(self.item_combobox.get())

    def _on_item_change(self, value):
        if self.type_index == 0:
            item = get_disc_by_name(value)
            if item:
                qty = get_stock_disc_quantity(item.doc_id)
                self.current_label.configure(text=f"Текущий остаток: {qty}")
            else:
                self.current_label.configure(text="Текущий остаток: 0")
        else:
            item = get_box_by_name(value)
            if item:
                qty = get_stock_box_quantity(item.doc_id)
                self.current_label.configure(text=f"Текущий остаток: {qty}")
            else:
                self.current_label.configure(text="Текущий остаток: 0")

    def ok(self):
        item_name = self.item_combobox.get().strip()
        quantity_str = self.quantity_entry.get().strip()
        reason = self.reason_entry.get().strip()

        if not item_name:
            messagebox.showerror("Ошибка", "Выберите носитель/коробку")
            return

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
            return

        component_type = 'disc' if self.type_index == 0 else 'box'
        item = get_disc_by_name(item_name) if self.type_index == 0 else get_box_by_name(item_name)
        if not item:
            messagebox.showerror("Ошибка", "Компонент не найден")
            return

        success, message = write_off_component(component_type, item.doc_id, quantity, reason)
        if not success:
            messagebox.showerror("Ошибка", message)
            return

        messagebox.showinfo("Успех", message)
        self.accepted = True
        self.destroy()

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
        self.accepted = False
        self.destroy()

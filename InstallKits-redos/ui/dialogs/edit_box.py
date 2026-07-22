"""
Диалог редактирования коробки.
"""

import customtkinter as ctk
from tkinter import messagebox
from data import update_box
from ui.dialogs.base_dialog import BaseDialog


class EditBoxDialog(BaseDialog):
    def get_default_geometry(self):
        return "350x200"

    def __init__(self, master, box, stock_tab=None):
        super().__init__(master)

        self.title("Редактировать коробку")

        self.grid_columnconfigure(0, weight=1)

        self.accepted = False
        self.box = box
        self.stock_tab = stock_tab

        # Название
        ctk.CTkLabel(self, text="Название:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.insert(0, box.get('name', ''))
        self.name_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Описание
        ctk.CTkLabel(self, text="Описание:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.desc_entry = ctk.CTkEntry(self)
        self.desc_entry.insert(0, box.get('description', ''))
        self.desc_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=4, column=0, padx=10, pady=10, sticky="e")

        ctk.CTkButton(button_frame, text="Отмена", command=self.cancel).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Сохранить", command=self.ok).pack(side="right", padx=5)

    def ok(self):
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()

        if not name:
            messagebox.showerror("Ошибка", "Введите название")
            return

        try:
            update_box(self.box.doc_id, name, description)
            self.accepted = True
            self.destroy()

            if self.stock_tab:
                self.stock_tab.load_stock()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def cancel(self):
        self.accepted = False
        self.destroy()

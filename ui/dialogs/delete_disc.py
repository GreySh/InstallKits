"""
Диалог удаления носителя.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from data import get_all_discs, delete_disc
from ui.dialogs.base_dialog import BaseDialog


class DeleteDiscDialog(BaseDialog):
    def get_default_geometry(self):
        return "300x200"
    
    def __init__(self, master, stock_tab=None, view_tab=None):
        super().__init__(master)
        
        self.title("Удалить носитель")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        self.accepted = False
        self.stock_tab = stock_tab
        self.view_tab = view_tab
        
        # Список носителей
        ctk.CTkLabel(self, text="Выберите носитель для удаления:").pack(padx=10, pady=10, anchor="w")
        
        discs = get_all_discs()
        disc_names = [disc['name'] for disc in discs]
        
        self.disc_combo = ctk.CTkComboBox(self, values=disc_names, state="readonly")
        self.disc_combo.pack(fill="x", padx=10, pady=5)
        if disc_names:
            self.disc_combo.set(disc_names[0])
        
        # Информация о диске
        self.info_label = ctk.CTkLabel(self, text="")
        self.info_label.pack(padx=10, pady=5, anchor="w")
        
        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(padx=10, pady=10, fill="x")
        
        self.cancel_button = ctk.CTkButton(button_frame, text="Отмена", command=self.cancel)
        self.cancel_button.pack(side="right", padx=5)
        
        self.delete_button = ctk.CTkButton(button_frame, text="Удалить", command=self.delete, fg_color="red")
        self.delete_button.pack(side="right", padx=5)
    
    def delete(self):
        """Удалить диск."""
        disc_name = self.disc_combo.get().strip()
        
        if not disc_name:
            messagebox.showerror("Ошибка", "Выберите носитель для удаления")
            return
        
        try:
            from data import get_disc_by_name
            disc = get_disc_by_name(disc_name)
            if disc:
                delete_disc(disc.doc_id)
                self.accepted = True
                self.destroy()
                
                # Обновить вкладки
                if self.stock_tab:
                    self.stock_tab.load_stock()
                if self.view_tab:
                    self.view_tab.load_all()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить носитель: {str(e)}")
    
    def cancel(self):
        """Обработать нажатие кнопки Cancel."""
        self.accepted = False
        self.destroy()

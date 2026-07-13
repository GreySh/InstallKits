"""
Диалог удаления коробки.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from data import get_all_boxes, delete_box
from ui.dialogs.base_dialog import BaseDialog


class DeleteBoxDialog(BaseDialog):
    def get_default_geometry(self):
        return "300x200"
    
    def __init__(self, master, stock_tab=None):
        super().__init__(master)
        
        self.title("Удалить коробку")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        self.accepted = False
        self.stock_tab = stock_tab
        
        # Список коробок
        ctk.CTkLabel(self, text="Выберите коробку для удаления:").pack(padx=10, pady=10, anchor="w")
        
        boxes = get_all_boxes()
        box_names = [box['name'] for box in boxes]
        
        self.box_combo = ctk.CTkComboBox(self, values=box_names, state="readonly")
        self.box_combo.pack(fill="x", padx=10, pady=5)
        if box_names:
            self.box_combo.set(box_names[0])
        
        # Информация о коробке
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
        """Удалить коробку."""
        box_name = self.box_combo.get().strip()
        
        if not box_name:
            messagebox.showerror("Ошибка", "Выберите коробку для удаления")
            return
        
        try:
            from data import get_box_by_name
            box = get_box_by_name(box_name)
            if box:
                delete_box(box.doc_id)
                self.accepted = True
                self.destroy()
                
                # Обновить вкладки
                if self.stock_tab:
                    self.stock_tab.load_stock()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить коробку: {str(e)}")
    
    def cancel(self):
        """Обработать нажатие кнопки Cancel."""
        self.accepted = False
        self.destroy()

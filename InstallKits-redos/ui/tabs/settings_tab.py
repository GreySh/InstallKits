"""
Вкладка настроек.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from settings_manager import get_db_path, set_db_path


class SettingsTab(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text="Настройки", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w"
        )
        
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        path_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(path_frame, text="Настройки базы данных", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w"
        )
        
        ctk.CTkLabel(path_frame, text="База данных:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.db_path_entry = ctk.CTkEntry(path_frame)
        self.db_path_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        self.db_browse_button = ctk.CTkButton(path_frame, text="Обзор", width=80, command=self.browse_db)
        self.db_browse_button.grid(row=1, column=2, padx=5, pady=5)
        
        save_frame = ctk.CTkFrame(self, fg_color="transparent")
        save_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="e")
        
        self.save_button = ctk.CTkButton(save_frame, text="Сохранить", command=self.save_settings)
        self.save_button.pack(side="right", padx=5)
        
        from version import VERSION
        ctk.CTkLabel(self, text=f"Версия: {VERSION}", font=("Arial", 11, "bold")).grid(
            row=3, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w"
        )
        
        self.load_current_settings()
    
    def load_current_settings(self):
        """Загрузить текущие настройки в поля ввода."""
        db_path = get_db_path()
        self.db_path_entry.delete(0, 'end')
        self.db_path_entry.insert(0, db_path)
    
    def browse_db(self):
        """Открыть диалог выбора файла базы данных."""
        file_path = filedialog.askopenfilename(
            title="Выберите файл базы данных",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.db_path_entry.get())
        )
        if file_path:
            self.db_path_entry.delete(0, 'end')
            self.db_path_entry.insert(0, file_path)
    
    def save_settings(self):
        """Сохранить настройки."""
        # Получаем путь из поля ввода
        db_path = self.db_path_entry.get().strip()
        
        if not db_path:
            messagebox.showerror("Ошибка", "Укажите путь к базе данных")
            return
        
        try:
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # Сохраняем путь в настройки
            set_db_path(db_path)
            
            messagebox.showinfo("Успех", "Настройки сохранены")
            
            # Перезагружаем настройки в поле ввода
            self.load_current_settings()
            
            # Перезагружаем базу данных
            from data.db import close_database, get_database
            close_database()
            get_database()
            
            # Уведомляем главное окно
            main_window = self.master.nametowidget('.')
            if hasattr(main_window, 'reload_tabs'):
                main_window.reload_tabs()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")

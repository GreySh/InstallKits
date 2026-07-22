"""
Базовый класс для диалогов с поддержкой запоминания позиции.
"""

import customtkinter as ctk
import tkinter as tk
import json
import os


class BaseDialog(tk.Toplevel):
    """Базовый класс для диалогов с запоминанием позиции."""
    
    window_geometries = {}
    
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.load_settings()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind('<Configure>', self.on_configure)
        
        class_name = self.__class__.__name__
        loaded_geometry = False
        if class_name in BaseDialog.window_geometries:
            geometry = BaseDialog.window_geometries[class_name]
            self.geometry(geometry)
            loaded_geometry = True
        else:
            default_geom = self.get_default_geometry()
            if 'x' in default_geom:
                self.geometry(default_geom)
        
        if not loaded_geometry:
            self.after(50, self.center_window)
    
    def get_default_geometry(self):
        return "400x300"
    
    def center_window(self):
        self.update_idletasks()
        
        try:
            self_width = self.winfo_width()
            self_height = self.winfo_height()
            
            if self_width <= 0 or self_height <= 0:
                self_width = self.winfo_reqwidth()
                self_height = self.winfo_reqheight()
            
            master_geom = self.master.geometry().split('+')
            master_size = master_geom[0].split('x')
            master_width = int(master_size[0])
            master_height = int(master_size[1])
            master_x = int(master_geom[1])
            master_y = int(master_geom[2])
            
            x = master_x + (master_width - self_width) // 2
            y = master_y + (master_height - self_height) // 2
            
            current_geom = self.geometry().split('+')[0]
            self.geometry(f'{current_geom}+{x}+{y}')
        except Exception as e:
            pass
    
    def on_configure(self, event):
        geometry = self.geometry()
        class_name = self.__class__.__name__
        BaseDialog.window_geometries[class_name] = geometry
    
    def on_close(self):
        geometry = self.geometry()
        class_name = self.__class__.__name__
        BaseDialog.window_geometries[class_name] = geometry
        self.save_settings()
        self.destroy()
    
    def load_settings(self):
        """Загрузить настройки из файла (каждый раз перечитываем, чтобы не терять данные MainWindow)."""
        try:
            from settings_manager import SETTINGS_FILE
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'window_geometries' in data:
                        BaseDialog.window_geometries.update(data['window_geometries'])
        except Exception as e:
            pass
    
    def save_settings(self):
        """Сохранить настройки в файл."""
        try:
            from settings_manager import SETTINGS_FILE
            
            # Читаем текущий файл
            current = {}
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    current = json.load(f)
            
            # Обновляем геометрии
            current['window_geometries'] = BaseDialog.window_geometries
            
            # Записываем
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(current, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
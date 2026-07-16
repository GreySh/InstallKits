"""
Главное окно приложения.
"""

import customtkinter as ctk
from version import VERSION
from ui.tabs.products_tab import ProductsTab
from ui.tabs.stock_tab import StockTab
from ui.tabs.settings_tab import SettingsTab
from ui.tabs.operations_tab import OperationsTab
from ui.tabs.batch_dispatch_tab import BatchDispatchTab
from data import get_all_products, get_all_discs, get_all_boxes, add_disc, add_box


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(f"Учет инсталляционных комплектов v{VERSION}")
        
        # Настраиваем тему
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Загружаем сохраненную геометрию
        self.load_geometry()
        
        # Порядок вкладок в боковой панели
        self.tab_order = ["Списание", "Состав ИК", "Остатки", "Настройки", "Операции"]
        
        # Создаем навигацию
        self.create_navigation()
        
        # Создаем вкладки
        self.create_tabs()
        
        # Привязать событие закрытия для сохранения позиции
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Привязать событие изменения размера для сохранения позиции
        self.bind('<Configure>', self.on_configure)
    
    def load_geometry(self):
        """Загрузить сохраненную геометрию."""
        try:
            import json
            import settings_manager
            settings_manager.load_settings()
            
            if 'window_geometries' in settings_manager._settings:
                geometries = settings_manager._settings['window_geometries']
                if 'MainWindow' in geometries:
                    self.geometry(geometries['MainWindow'])
        except Exception as e:
            pass
    
    def save_settings(self):
        """Сохранить настройки в файл."""
        try:
            import os
            import json
            import settings_manager
            from ui.dialogs.base_dialog import BaseDialog
            
            # Читаем текущий файл
            current = {}
            if os.path.exists(settings_manager.SETTINGS_FILE):
                with open(settings_manager.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    current = json.load(f)
            
            # Обновляем геометрии: диалоги + MainWindow
            geometries = current.get('window_geometries', {})
            geometries.update(BaseDialog.window_geometries)
            geometries['MainWindow'] = self.geometry()
            current['window_geometries'] = geometries
            BaseDialog.window_geometries = geometries
            
            # Сохраняем
            with open(settings_manager.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(current, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
    
    def reload_tabs(self):
        """Перезагрузить все вкладки."""
        # Перезагрузить данные в вкладках
        if "Состав ИК" in self.tabs:
            self.tabs["Состав ИК"].load_all()
        if "Остатки" in self.tabs:
            self.tabs["Остатки"].load_all()
        if "Операции" in self.tabs:
            self.tabs["Операции"].load_operations()
        if "Списание" in self.tabs:
            self.tabs["Списание"].load_all()
    
    def on_configure(self, event):
        """Сохранить геометрию при изменении размера или позиции."""
        self.save_settings()
    
    def on_close(self):
        """Сохранить настройки при закрытии."""
        self.save_settings()
        self.destroy()
    
    def create_navigation(self):
        """Создать боковую панель переключения вкладок."""
        self.sidebar = ctk.CTkFrame(self, width=180)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        self.sidebar.pack_propagate(False)

        self.tab_buttons = {}
        for name in self.tab_order:
            btn = ctk.CTkButton(
                self.sidebar,
                text=name,
                command=lambda n=name: self.show_tab(n),
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.tab_buttons[name] = btn
        
    
    def create_tabs(self):
        """Создать вкладки."""
        self.content = ctk.CTkFrame(self)
        self.content.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        
        self.tabs = {
            "Списание": BatchDispatchTab,
            "Состав ИК": ProductsTab,
            "Остатки": StockTab,
            "Настройки": SettingsTab,
            "Операции": OperationsTab,
        }
        
        for name, tab_cls in self.tabs.items():
            self.tabs[name] = tab_cls(self.content)
            self.tabs[name].grid(row=0, column=0, sticky="nsew")
            self.tabs[name].grid_remove()
        
        self.show_tab("Списание")
    
    def show_tab(self, name):
        """Показать выбранную вкладку."""
        for n, frame in self.tabs.items():
            if n == name:
                frame.grid()
            else:
                frame.grid_remove()
        for n, btn in self.tab_buttons.items():
            if n == name:
                btn.configure(fg_color="#1f6feb", hover_color="#1a5fce")
            else:
                btn.configure(fg_color=("gray75", "gray25"), hover_color=("gray70", "gray30"))



if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

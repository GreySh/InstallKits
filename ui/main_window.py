"""
Главное окно приложения.
"""

import customtkinter as ctk
from ui.tabs.products_tab import ProductsTab
from ui.tabs.stock_tab import StockTab
from ui.tabs.settings_tab import SettingsTab
from ui.tabs.operations_tab import OperationsTab
from ui.tabs.batch_dispatch_tab import BatchDispatchTab
from ui.report_window import ReportWindow
from ui.dialogs.dispatch import DispatchDialog
from data import get_all_products, get_all_discs, get_all_boxes, add_disc, add_box


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Учет инсталляционных комплектов")
        
        # Настраиваем тему
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Загружаем сохраненную геометрию
        self.load_geometry()
        
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
        if hasattr(self, 'products_tab'):
            self.products_tab.load_all()
        if hasattr(self, 'stock_tab'):
            self.stock_tab.load_all()
        if hasattr(self, 'operations_tab'):
            self.operations_tab.load_operations()
        if hasattr(self, 'batch_dispatch_tab'):
            self.batch_dispatch_tab.load_all()
    
    def on_configure(self, event):
        """Сохранить геометрию при изменении размера или позиции."""
        self.save_settings()
    
    def on_close(self):
        """Сохранить настройки при закрытии."""
        self.save_settings()
        self.destroy()
    
    def create_navigation(self):
        """Создать панель навигации."""
        self.nav_frame = ctk.CTkFrame(self, width=200)
        self.nav_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        # Кнопка отчетов
        self.report_button = ctk.CTkButton(
            self.nav_frame,
            text="Отчеты",
            command=self.open_report_window,
            width=150
        )
        self.report_button.pack(pady=10)
        
        # Кнопка списания
        self.dispatch_button = ctk.CTkButton(
            self.nav_frame,
            text="Списать ИК",
            command=self.open_dispatch_dialog,
            width=150
        )
        self.dispatch_button.pack(pady=10)
    
    def create_tabs(self):
        """Создать вкладки."""
        self.tabview = ctk.CTkTabview(self, width=750, height=600)
        self.tabview.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Вкладка пакетного списания (основная)
        self.batch_dispatch_tab = BatchDispatchTab(self.tabview.add("Списание"))
        self.batch_dispatch_tab.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Списание").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Списание").grid_rowconfigure(0, weight=1)
        
        # Вкладка продуктов
        self.products_tab = ProductsTab(self.tabview.add("Состав ИК"))
        self.products_tab.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Состав ИК").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Состав ИК").grid_rowconfigure(0, weight=1)
        
        # Вкладка остатков
        self.stock_tab = StockTab(self.tabview.add("Остатки"))
        self.stock_tab.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Остатки").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Остатки").grid_rowconfigure(0, weight=1)
        
        # Вкладка настроек
        self.settings_tab = SettingsTab(self.tabview.add("Настройки"))
        self.settings_tab.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Настройки").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Настройки").grid_rowconfigure(0, weight=1)
        
        # Вкладка операций
        self.operations_tab = OperationsTab(self.tabview.add("Операции"))
        self.operations_tab.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Операции").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Операции").grid_rowconfigure(0, weight=1)
    
    def open_report_window(self):
        """Открыть окно отчетов."""
        ReportWindow(self)
    
    def open_dispatch_dialog(self):
        """Открыть диалог списания комплекта."""
        DispatchDialog(self, self.stock_tab)
    


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

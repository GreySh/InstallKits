"""
Главное окно приложения.
"""

import customtkinter as ctk
from ui.tabs.products_tab import ProductsTab
from ui.tabs.stock_tab import StockTab
from ui.tabs.view_stock_tab import ViewStockTab
from ui.report_window import ReportWindow
from ui.dialogs.dispatch import DispatchDialog
from data import get_all_products, get_all_discs, get_all_boxes, add_disc, add_box


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Учет инсталляционных комплектов")
        self.geometry("1000x700")
        
        # Настраиваем тему
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Создаем навигацию
        self.create_navigation()
        
        # Создаем вкладки
        self.create_tabs()
    
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
            text="Списание",
            command=self.open_dispatch_dialog,
            width=150
        )
        self.dispatch_button.pack(pady=10)
    
    def create_tabs(self):
        """Создать вкладки."""
        self.tabview = ctk.CTkTabview(self, width=750, height=600)
        self.tabview.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Вкладка продуктов
        self.products_tab = ProductsTab(self.tabview.add("Продукты"))
        self.products_tab.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Продукты").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Продукты").grid_rowconfigure(0, weight=1)
        
        # Вкладка остатков
        self.stock_tab = StockTab(self.tabview.add("Остатки"))
        self.stock_tab.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Остатки").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Остатки").grid_rowconfigure(0, weight=1)
        
        # Вкладка просмотра
        self.view_stock_tab = ViewStockTab(self.tabview.add("Просмотр"))
        self.view_stock_tab.grid(row=0, column=0, sticky="nsew")
        self.tabview.tab("Просмотр").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Просмотр").grid_rowconfigure(0, weight=1)
    
    def open_report_window(self):
        """Открыть окно отчетов."""
        ReportWindow(self)
    
    def open_dispatch_dialog(self):
        """Открыть диалог списания комплекта."""
        DispatchDialog(self, self.stock_tab, self.view_stock_tab)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

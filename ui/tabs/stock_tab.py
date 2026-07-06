"""
Вкладка управления остатками.
"""

import customtkinter as ctk
from tkinter import ttk
from data import get_all_discs, get_all_boxes, add_disc, add_box
from ui.dialogs.add_disc import AddDiscDialog
from ui.dialogs.add_box import AddBoxDialog
from ui.dialogs.add_all import AddAllDialog
from ui.dialogs.adjust_stock import AdjustStockDialog
from ui.dialogs.delete_disc import DeleteDiscDialog
from ui.dialogs.delete_box import DeleteBoxDialog


class StockTab(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Заголовок
        self.title_label = ctk.CTkLabel(self, text="Управление остатками", font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="w")
        
        # Кнопки добавления
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="w")
        
        self.add_disc_button = ctk.CTkButton(button_frame, text="Новый диск", command=self.add_disc)
        self.add_disc_button.pack(side="left", padx=5)
        
        self.add_box_button = ctk.CTkButton(button_frame, text="Новая коробка", command=self.add_box)
        self.add_box_button.pack(side="left", padx=5)
        
        self.add_all_button = ctk.CTkButton(button_frame, text="Диски/Коробки", command=self.add_all)
        self.add_all_button.pack(side="left", padx=5)
        
        self.adjust_button = ctk.CTkButton(button_frame, text="Корректировка", command=self.adjust_stock)
        self.adjust_button.pack(side="left", padx=5)
        
        self.delete_disc_button = ctk.CTkButton(button_frame, text="Удалить диск", command=self.delete_disc, fg_color="red")
        self.delete_disc_button.pack(side="left", padx=5)
        
        self.delete_box_button = ctk.CTkButton(button_frame, text="Удалить коробку", command=self.delete_box, fg_color="red")
        self.delete_box_button.pack(side="left", padx=5)
        
        # Таблица остатков
        self.stock_tree = ttk.Treeview(self, columns=("name", "quantity"), show="tree headings")
        self.stock_tree.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        
        # Заголовки колонок
        self.stock_tree.heading("#0", text="Тип")
        self.stock_tree.heading("name", text="Название")
        self.stock_tree.heading("quantity", text="Количество")
        
        # Загрузить остатки
        self.load_stock()
    
    def load_stock(self):
        """Загрузить остатки в таблицу."""
        # Очистить таблицу
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        # Загрузить диски
        from data import get_all_stock_discs
        discs = get_all_stock_discs()
        for disc in discs:
            self.stock_tree.insert("", "end", text="Диск", values=(disc['disc_name'], disc['quantity']))
        
        # Загрузить коробки
        from data import get_all_stock_boxes
        boxes = get_all_stock_boxes()
        for box in boxes:
            self.stock_tree.insert("", "end", text="Коробка", values=(box['box_name'], box['quantity']))
    
    def add_disc(self):
        """Открыть диалог добавления нового диска."""
        # Получить ссылку на view_tab из главного окна
        view_tab = None
        # Получить корневой виджет (MainWindow)
        root = self.master.nametowidget('.')
        if hasattr(root, 'view_stock_tab'):
            view_tab = root.view_stock_tab
        dialog = AddDiscDialog(self.master, self, view_tab)
        if dialog.accepted:
            self.load_stock()
    
    def add_box(self):
        """Открыть диалог добавления новой коробки."""
        # Получить ссылку на view_tab из главного окна
        view_tab = None
        # Получить корневой виджет (MainWindow)
        root = self.master.nametowidget('.')
        if hasattr(root, 'view_stock_tab'):
            view_tab = root.view_stock_tab
        dialog = AddBoxDialog(self.master, self, view_tab)
        if dialog.accepted:
            self.load_stock()
    
    def add_all(self):
        """Открыть диалог добавления дисков/коробок."""
        # Получить ссылку на view_tab из главного окна
        view_tab = None
        # Получить корневой виджет (MainWindow)
        root = self.master.nametowidget('.')
        if hasattr(root, 'view_stock_tab'):
            view_tab = root.view_stock_tab
        dialog = AddAllDialog(self.master, self, view_tab)
        if dialog.accepted:
            self.load_stock()
    
    def adjust_stock(self):
        """Открыть диалог корректировки остатков."""
        # Получить ссылку на view_tab из главного окна
        view_tab = None
        # Получить корневой виджет (MainWindow)
        root = self.master.nametowidget('.')
        if hasattr(root, 'view_stock_tab'):
            view_tab = root.view_stock_tab
        dialog = AdjustStockDialog(self.master, self, view_tab)
        if dialog.accepted:
            self.load_stock()
    
    def delete_disc(self):
        """Открыть диалог удаления диска."""
        # Получить ссылку на view_tab из главного окна
        view_tab = None
        # Получить корневой виджет (MainWindow)
        root = self.master.nametowidget('.')
        if hasattr(root, 'view_stock_tab'):
            view_tab = root.view_stock_tab
        dialog = DeleteDiscDialog(self.master, self, view_tab)
        if dialog.accepted:
            self.load_stock()
    
    def delete_box(self):
        """Открыть диалог удаления коробки."""
        # Получить ссылку на view_tab из главного окна
        view_tab = None
        # Получить корневой виджет (MainWindow)
        root = self.master.nametowidget('.')
        if hasattr(root, 'view_stock_tab'):
            view_tab = root.view_stock_tab
        dialog = DeleteBoxDialog(self.master, self, view_tab)
        if dialog.accepted:
            self.load_stock()

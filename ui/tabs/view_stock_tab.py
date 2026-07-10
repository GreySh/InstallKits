"""
Вкладка просмотра остатков.
"""

import customtkinter as ctk
from tkinter import ttk
from data import (
    get_all_products, get_product_components, get_stock_disc_quantity,
    get_stock_box_quantity, get_all_stock_discs, get_all_stock_boxes
)


class ViewStockTab(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Создаем вкладки внутри вкладки
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew")
        
        # Вкладка продуктов
        self.tabview.add("Продукты")
        self.products_frame = self.tabview.tab("Продукты")
        self.products_frame.grid_columnconfigure(0, weight=1)
        self.products_frame.grid_rowconfigure(1, weight=1)
        
        # Вкладка носителей
        self.tabview.add("Носитель")
        self.discs_frame = self.tabview.tab("Носитель")
        self.discs_frame.grid_columnconfigure(0, weight=1)
        self.discs_frame.grid_rowconfigure(1, weight=1)
        
        # Вкладка коробок
        self.tabview.add("Коробки")
        self.boxes_frame = self.tabview.tab("Коробки")
        self.boxes_frame.grid_columnconfigure(0, weight=1)
        self.boxes_frame.grid_rowconfigure(1, weight=1)
        
        # Заголовки
        ctk.CTkLabel(self.products_frame, text="Остатки по продуктам", font=("Arial", 14, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        ctk.CTkLabel(self.discs_frame, text="Остатки по носителям", font=("Arial", 14, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        ctk.CTkLabel(self.boxes_frame, text="Остатки по коробкам", font=("Arial", 14, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        
        # Таблица продуктов
        self.products_tree = ttk.Treeview(self.products_frame, columns=("available",), show="tree headings")
        self.products_tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.products_tree.heading("#0", text="Название", command=lambda: self.sort_products("name"))
        self.products_tree.heading("available", text="Доступно комплектов", command=lambda: self.sort_products("available"))
        
        # Настройка ширин колонок
        self.products_tree.column("#0", width=100, anchor="w")
        self.products_tree.column("available", width=200, anchor="w")
        
        # Таблица носителей
        self.discs_tree = ttk.Treeview(self.discs_frame, columns=("quantity",), show="tree headings")
        self.discs_tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.discs_tree.heading("#0", text="Название", command=lambda: self.sort_discs("name"))
        self.discs_tree.heading("quantity", text="Остаток", command=lambda: self.sort_discs("quantity"))
        
        # Настройка ширин колонок
        self.discs_tree.column("#0", width=100, anchor="w")
        self.discs_tree.column("quantity", width=200, anchor="w")
        
        # Таблица коробок
        self.boxes_tree = ttk.Treeview(self.boxes_frame, columns=("quantity",), show="tree headings")
        self.boxes_tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.boxes_tree.heading("#0", text="Название", command=lambda: self.sort_boxes("name"))
        self.boxes_tree.heading("quantity", text="Остаток", command=lambda: self.sort_boxes("quantity"))
        
        # Настройка ширин колонок
        self.boxes_tree.column("#0", width=100, anchor="w")
        self.boxes_tree.column("quantity", width=200, anchor="w")
        
        # Состояния сортировки
        self.products_sort_column = "name"
        self.products_sort_reverse = False
        self.discs_sort_column = "name"
        self.discs_sort_reverse = False
        self.boxes_sort_column = "name"
        self.boxes_sort_reverse = False
        
        # Загрузить остатки
        self.load_all()
    
    def sort_products(self, column):
        """Сортировка таблицы продуктов."""
        if self.products_sort_column == column:
            self.products_sort_reverse = not self.products_sort_reverse
        else:
            self.products_sort_column = column
            self.products_sort_reverse = False
        
        items = []
        for item_id in self.products_tree.get_children():
            item = self.products_tree.item(item_id)
            items.append((item_id, item['text'], item['values']))
        
        if column == "name":
            items.sort(key=lambda x: x[1], reverse=self.products_sort_reverse)
        elif column == "available":
            items.sort(key=lambda x: x[2][0], reverse=self.products_sort_reverse)
        
        for item_id in self.products_tree.get_children():
            self.products_tree.delete(item_id)
        
        for item_id, text, values in items:
            self.products_tree.insert("", "end", text=text, values=values)
    
    def sort_discs(self, column):
        """Сортировка таблицы носителей."""
        if self.discs_sort_column == column:
            self.discs_sort_reverse = not self.discs_sort_reverse
        else:
            self.discs_sort_column = column
            self.discs_sort_reverse = False
        
        items = []
        for item_id in self.discs_tree.get_children():
            item = self.discs_tree.item(item_id)
            items.append((item_id, item['text'], item['values']))
        
        if column == "name":
            items.sort(key=lambda x: x[1], reverse=self.discs_sort_reverse)
        elif column == "quantity":
            items.sort(key=lambda x: x[2][0], reverse=self.discs_sort_reverse)
        
        for item_id in self.discs_tree.get_children():
            self.discs_tree.delete(item_id)
        
        for item_id, text, values in items:
            self.discs_tree.insert("", "end", text=text, values=values)
    
    def sort_boxes(self, column):
        """Сортировка таблицы коробок."""
        if self.boxes_sort_column == column:
            self.boxes_sort_reverse = not self.boxes_sort_reverse
        else:
            self.boxes_sort_column = column
            self.boxes_sort_reverse = False
        
        items = []
        for item_id in self.boxes_tree.get_children():
            item = self.boxes_tree.item(item_id)
            items.append((item_id, item['text'], item['values']))
        
        if column == "name":
            items.sort(key=lambda x: x[1], reverse=self.boxes_sort_reverse)
        elif column == "quantity":
            items.sort(key=lambda x: x[2][0], reverse=self.boxes_sort_reverse)
        
        for item_id in self.boxes_tree.get_children():
            self.boxes_tree.delete(item_id)
        
        for item_id, text, values in items:
            self.boxes_tree.insert("", "end", text=text, values=values)
    
    def load_all(self):
        """Загрузить все остатки."""
        self.load_products()
        self.load_discs()
        self.load_boxes()
    
    def load_products(self):
        """Загрузить остатки по продуктам."""
        # Очистить таблицу
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Загрузить продукты
        products = get_all_products()
        for product in products:
            product_id = product.doc_id
            name = product['name']
            components = get_product_components(product_id)
            
            # Определить минимальное доступное количество комплектов
            min_quantity = float('inf')
            for comp in components:
                disc_qty = get_stock_disc_quantity(comp['disc_id']) if comp['disc_id'] else float('inf')
                box_qty = get_stock_box_quantity(comp['box_id']) if comp['box_id'] else float('inf')
                
                if comp['disc_id'] and comp['disc_quantity'] > 0:
                    disc_qty //= comp['disc_quantity']
                if comp['box_id'] and comp['box_quantity'] > 0:
                    box_qty //= comp['box_quantity']
                
                min_quantity = min(min_quantity, disc_qty, box_qty)
            
            if min_quantity == float('inf'):
                min_quantity = 0
            
            self.products_tree.insert("", "end", text=name, values=(int(min_quantity),))
    
    def load_discs(self):
        """Загрузить остатки по носителям."""
        # Очистить таблицу
        for item in self.discs_tree.get_children():
            self.discs_tree.delete(item)
        
        # Загрузить носители
        discs = get_all_stock_discs()
        for disc in discs:
            self.discs_tree.insert("", "end", text=disc['disc_name'], values=(disc['quantity'],))
    
    def load_boxes(self):
        """Загрузить остатки по коробкам."""
        # Очистить таблицу
        for item in self.boxes_tree.get_children():
            self.boxes_tree.delete(item)
        
        # Загрузить коробки
        boxes = get_all_stock_boxes()
        for box in boxes:
            self.boxes_tree.insert("", "end", text=box['box_name'], values=(box['quantity'],))

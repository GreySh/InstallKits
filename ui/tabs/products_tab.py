"""
Вкладка управления продуктами.
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from data import get_all_products, get_product_components, delete_product, get_disc_by_id, get_box_by_id
from ui.dialogs.add_product import AddProductDialog
from ui.dialogs.edit_product import EditProductDialog


class ProductsTab(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Заголовок
        self.title_label = ctk.CTkLabel(self, text="Управление продуктами", font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Кнопка добавления
        self.add_button = ctk.CTkButton(self, text="Добавить продукт", command=self.add_product)
        self.add_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        # Таблица продуктов
        self.products_tree = ttk.Treeview(self, columns=("name", "components"), show="tree headings")
        self.products_tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Заголовки колонок
        self.products_tree.heading("#0", text="ID")
        self.products_tree.heading("name", text="Название")
        self.products_tree.heading("components", text="Компоненты")
        
        # Кнопка редактирования
        self.edit_button = ctk.CTkButton(self, text="Редактировать", command=self.edit_product)
        self.edit_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        # Кнопка удаления
        self.delete_button = ctk.CTkButton(self, text="Удалить", command=self.delete_product)
        self.delete_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        
        # Загрузить продукты
        self.load_products()
    
    def load_products(self):
        """Загрузить продукты в таблицу."""
        # Очистить таблицу
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Загрузить продукты
        products = get_all_products()
        for product in products:
            product_id = product.doc_id
            name = product['name']
            components = get_product_components(product_id)
            
            # Сформировать строку компонентов
            components_str = []
            for comp in components:
                comp_details = []
                if comp['disc_id']:
                    from data import get_disc_by_id
                    disc = get_disc_by_id(comp['disc_id'])
                    if disc:
                        comp_details.append(f"{disc['name']} x{comp['disc_quantity']}")
                if comp['box_id']:
                    from data import get_box_by_id
                    box = get_box_by_id(comp['box_id'])
                    if box:
                        comp_details.append(f"{box['name']} x{comp['box_quantity']}")
                components_str.append(", ".join(comp_details))
            
            components_text = "; ".join(components_str)
            
            self.products_tree.insert("", "end", text=str(product_id), values=(name, components_text))
    
    def add_product(self):
        """Открыть диалог добавления продукта."""
        root = self.winfo_toplevel()
        dialog = AddProductDialog(root)
        if getattr(dialog, 'accepted', False):
            self.load_products()
    
    def edit_product(self):
        """Открыть диалог редактирования продукта."""
        root = self.winfo_toplevel()
        selected = self.products_tree.selection()
        if not selected:
            return
        
        item = self.products_tree.item(selected[0])
        product_id = int(item['text'])
        
        dialog = EditProductDialog(root, product_id)
        if getattr(dialog, 'accepted', False):
            self.load_products()
    
    def delete_product(self):
        """Удалить выбранный продукт."""
        selected = self.products_tree.selection()
        if not selected:
            return
        
        item = self.products_tree.item(selected[0])
        product_id = int(item['text'])
        
        # Подтверждение удаления
        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить продукт?")
        
        if confirm:
            delete_product(product_id)
            self.load_products()

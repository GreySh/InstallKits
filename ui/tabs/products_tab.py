"""
Вкладка управления продуктами.
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from data import (
    get_all_products, get_product_components, delete_product,
    get_disc_by_id, get_box_by_id,
    get_stock_disc_quantity, get_stock_box_quantity,
)
from ui.dialogs.add_product import AddProductDialog
from ui.dialogs.edit_product import EditProductDialog


class ProductsTab(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Заголовок
        self.title_label = ctk.CTkLabel(self, text="Управление комплектами", font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Кнопка добавления
        self.add_button = ctk.CTkButton(self, text="Добавить комплект", command=self.add_product)
        self.add_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        # Таблица продуктов
        self.products_tree = ttk.Treeview(self, columns=("name", "available", "components"), show="tree headings")
        self.products_tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Заголовки колонок
        self.products_tree.heading("#0", text="ID")
        self.products_tree.heading("name", text="Название", command=lambda: self.sort_by("name"))
        self.products_tree.heading("available", text="Доступно", command=lambda: self.sort_by("available"))
        self.products_tree.heading("components", text="Компоненты")
        
        # Настройка ширин колонок
        self.products_tree.column("#0", width=5, anchor="center")
        self.products_tree.column("name", width=50, anchor="w")
        self.products_tree.column("available", width=80, anchor="center")
        self.products_tree.column("components", width=300, anchor="w")
        
        # Состояние сортировки
        self.sort_column = "name"
        self.sort_reverse = False
        
        # Кнопка редактирования
        self.edit_button = ctk.CTkButton(self, text="Редактировать", command=self.edit_product)
        self.edit_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        # Кнопка удаления
        self.delete_button = ctk.CTkButton(self, text="Удалить", command=self.delete_product, fg_color="red")
        self.delete_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        
        # Двойной клик — редактирование комплекта
        self.products_tree.bind("<Double-1>", self._on_double_click)

        # Загрузить продукты
        self.load_products()

    def _on_double_click(self, event):
        """Открыть редактирование по двойному клику по строке."""
        item = self.products_tree.identify_row(event.y)
        if item:
            self.products_tree.selection_set(item)
            self.edit_product()
    
    def sort_by(self, column):
        """Сортировка по колонке."""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Получить все элементы
        items = []
        for item_id in self.products_tree.get_children():
            item = self.products_tree.item(item_id)
            items.append((item_id, item['text'], item['values']))
        
        # Сортировать
        if column == "name":
            items.sort(key=lambda x: x[2][0], reverse=self.sort_reverse)
        elif column == "available":
            items.sort(key=lambda x: x[2][1], reverse=self.sort_reverse)
        elif column == "components":
            items.sort(key=lambda x: x[2][2], reverse=self.sort_reverse)
        
        # Очистить и пересоздать
        for item_id in self.products_tree.get_children():
            self.products_tree.delete(item_id)
        
        for item_id, text, values in items:
            self.products_tree.insert("", "end", text=text, values=values)
    
    def load_products(self):
        """Загрузить продукты в таблицу."""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        products = get_all_products()
        for product in products:
            product_id = product.doc_id
            name = product['name']
            components = get_product_components(product_id)
            
            components_str = []
            min_quantity = float('inf')
            for comp in components:
                comp_details = []
                if comp['disc_id']:
                    disc = get_disc_by_id(comp['disc_id'])
                    if disc:
                        comp_details.append(f"{disc['name']} x{comp['disc_quantity']}")
                        disc_qty = get_stock_disc_quantity(comp['disc_id'])
                        if comp['disc_quantity'] > 0:
                            disc_qty //= comp['disc_quantity']
                        min_quantity = min(min_quantity, disc_qty)
                if comp['box_id']:
                    box = get_box_by_id(comp['box_id'])
                    if box:
                        comp_details.append(f"{box['name']} x{comp['box_quantity']}")
                        box_qty = get_stock_box_quantity(comp['box_id'])
                        if comp['box_quantity'] > 0:
                            box_qty //= comp['box_quantity']
                        min_quantity = min(min_quantity, box_qty)
                components_str.append(", ".join(comp_details))
            
            components_text = "; ".join(components_str)
            available = int(min_quantity) if min_quantity != float('inf') else 0
            
            self.products_tree.insert("", "end", text=str(product_id), values=(name, available, components_text))
    
    def load_all(self):
        """Загрузить все данные (для перезагрузки после изменения настроек)."""
        self.load_products()
    
    def add_product(self):
        """Открыть диалог добавления продукта."""
        root = self.winfo_toplevel()
        dialog = AddProductDialog(root)
        self.wait_window(dialog)
        if getattr(dialog, 'accepted', False):
            self.load_products()
            self._refresh_operations()
    
    def edit_product(self):
        """Открыть диалог редактирования продукта."""
        root = self.winfo_toplevel()
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите комплект для редактирования")
            return
        
        item = self.products_tree.item(selected[0])
        product_id = int(item['text'])
        
        dialog = EditProductDialog(root, product_id)
        self.wait_window(dialog)
        if getattr(dialog, 'accepted', False):
            self.load_products()
            self._refresh_operations()

    def _refresh_operations(self):
        """Обновить зависимые вкладки (Списание, Операции) после изменения комплектов."""
        try:
            main_window = self.master.nametowidget('.')
            if hasattr(main_window, 'tabs'):
                if "Списание" in main_window.tabs:
                    main_window.tabs["Списание"].load_all()
                if "Операции" in main_window.tabs:
                    main_window.tabs["Операции"].load_operations()
        except Exception:
            pass
    
    def delete_product(self):
        """Удалить выбранный продукт."""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите комплект для удаления")
            return
        
        item = self.products_tree.item(selected[0])
        product_id = int(item['text'])
        product_name = item['values'][0]
        
        # Подтверждение удаления
        confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить продукт \"{product_name}\"?")
        
        if confirm:
            delete_product(product_id)
            self.load_products()

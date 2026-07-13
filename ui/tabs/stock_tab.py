"""
Вкладка управления остатками с подвкладками: Носители, Коробки, Продукты.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from data import (
    get_all_stock_discs, get_all_stock_boxes, get_all_discs, get_all_boxes,
    delete_disc, delete_box,
    get_all_products, get_product_components,
    get_stock_disc_quantity, get_stock_box_quantity,
    adjust_stock_disc, adjust_stock_box,
    get_disc_by_name, get_box_by_name,
)
from ui.dialogs.add_all import AddAllDialog
from ui.dialogs.adjust_stock import AdjustStockDialog
from ui.dialogs.add_stock import AddStockDialog
from ui.dialogs.add_component import AddComponentDialog
from ui.dialogs.write_off import WriteOffDialog


class StockTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Подвкладки
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        # --- Вкладка Носители ---
        self.tabview.add("Носители")
        self.discs_frame = self.tabview.tab("Носители")
        self.discs_frame.grid_columnconfigure(0, weight=1)
        self.discs_frame.grid_rowconfigure(2, weight=1)

        discs_btn_frame = ctk.CTkFrame(self.discs_frame)
        discs_btn_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(discs_btn_frame, text="Добавить", command=self.add_all).pack(side="left", padx=5)
        ctk.CTkButton(discs_btn_frame, text="Редактировать", command=self.edit_disc_stock).pack(side="left", padx=5)
        ctk.CTkButton(discs_btn_frame, text="Брак", fg_color="red", command=self.write_off_disc).pack(side="left", padx=5)

        self.discs_tree = ttk.Treeview(self.discs_frame, columns=("name", "quantity"), show="tree headings")
        self.discs_tree.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        self.discs_tree.heading("#0", text="", anchor="w")
        self.discs_tree.heading("name", text="Название", command=lambda: self._sort_tree(self.discs_tree, "name"))
        self.discs_tree.heading("quantity", text="Количество", command=lambda: self._sort_tree(self.discs_tree, "quantity"))
        self.discs_tree.column("#0", width=0, stretch=False)
        self.discs_tree.column("name", width=250, anchor="w")
        self.discs_tree.column("quantity", width=80, anchor="center")

        discs_bottom = ctk.CTkFrame(self.discs_frame)
        discs_bottom.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkButton(discs_bottom, text="Новый компонент", command=self.add_component_disc).pack(side="left", padx=5)
        ctk.CTkButton(discs_bottom, text="Удалить", command=self.delete_disc_component, fg_color="red").pack(side="right", padx=5)

        self.discs_tree.bind("<Double-1>", lambda e: self._on_double_click(e, "disc"))

        # --- Вкладка Коробки ---
        self.tabview.add("Коробки")
        self.boxes_frame = self.tabview.tab("Коробки")
        self.boxes_frame.grid_columnconfigure(0, weight=1)
        self.boxes_frame.grid_rowconfigure(2, weight=1)

        boxes_btn_frame = ctk.CTkFrame(self.boxes_frame)
        boxes_btn_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(boxes_btn_frame, text="Добавить", command=self.add_all).pack(side="left", padx=5)
        ctk.CTkButton(boxes_btn_frame, text="Редактировать", command=self.edit_box_stock).pack(side="left", padx=5)
        ctk.CTkButton(boxes_btn_frame, text="Брак", fg_color="red", command=self.write_off_box).pack(side="left", padx=5)

        self.boxes_tree = ttk.Treeview(self.boxes_frame, columns=("name", "quantity"), show="tree headings")
        self.boxes_tree.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        self.boxes_tree.heading("#0", text="", anchor="w")
        self.boxes_tree.heading("name", text="Название", command=lambda: self._sort_tree(self.boxes_tree, "name"))
        self.boxes_tree.heading("quantity", text="Количество", command=lambda: self._sort_tree(self.boxes_tree, "quantity"))
        self.boxes_tree.column("#0", width=0, stretch=False)
        self.boxes_tree.column("name", width=250, anchor="w")
        self.boxes_tree.column("quantity", width=80, anchor="center")

        boxes_bottom = ctk.CTkFrame(self.boxes_frame)
        boxes_bottom.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkButton(boxes_bottom, text="Новый компонент", command=self.add_component_box).pack(side="left", padx=5)
        ctk.CTkButton(boxes_bottom, text="Удалить", command=self.delete_box_component, fg_color="red").pack(side="right", padx=5)

        self.boxes_tree.bind("<Double-1>", lambda e: self._on_double_click(e, "box"))

        # --- Вкладка Комплекты ---
        self.tabview.add("Комплекты")
        self.products_frame = self.tabview.tab("Комплекты")
        self.products_frame.grid_columnconfigure(0, weight=1)
        self.products_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.products_frame, text="Доступные комплекты", font=("Arial", 14, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        self.products_tree = ttk.Treeview(self.products_frame, columns=("available",), show="tree headings")
        self.products_tree.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        self.products_tree.heading("#0", text="Название", command=lambda: self._sort_tree(self.products_tree, "name"))
        self.products_tree.heading("available", text="Доступно комплектов", command=lambda: self._sort_tree(self.products_tree, "available"))
        self.products_tree.column("#0", width=250, anchor="w")
        self.products_tree.column("available", width=150, anchor="center")

        # Загрузить данные
        self.load_all()

    # ─── Загрузка данных ────────────────────────────────────────

    def load_all(self):
        """Загрузить все данные (диски, коробки, продукты)."""
        self.load_discs()
        self.load_boxes()
        self.load_products()

    load_stock = load_all

    def load_discs(self):
        for item in self.discs_tree.get_children():
            self.discs_tree.delete(item)
        for disc in get_all_stock_discs():
            self.discs_tree.insert("", "end", text="", values=(disc['disc_name'], disc['quantity']))

    def load_boxes(self):
        for item in self.boxes_tree.get_children():
            self.boxes_tree.delete(item)
        for box in get_all_stock_boxes():
            self.boxes_tree.insert("", "end", text="", values=(box['box_name'], box['quantity']))

    def load_products(self):
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        for product in get_all_products():
            product_id = product.doc_id
            name = product['name']
            components = get_product_components(product_id)
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

    # ─── Сортировка ─────────────────────────────────────────────

    def _sort_tree(self, tree, column):
        items = [(tree.item(i)['text'], tree.item(i)['values'], i) for i in tree.get_children()]
        reverse = getattr(tree, '_sort_reverse', False)
        if getattr(tree, '_sort_column', None) == column:
            reverse = not reverse
        else:
            reverse = False
        tree._sort_column = column
        tree._sort_reverse = reverse

        col_idx = {"name": 0, "quantity": 1, "available": 0}.get(column, 0)
        items.sort(key=lambda x: x[1][col_idx] if x[1] else x[0], reverse=reverse)
        for i in tree.get_children():
            tree.delete(i)
        for text, values, _ in items:
            tree.insert("", "end", text=text, values=values)

    def _on_double_click(self, event, comp_type):
        """Редактирование количества по двойному клику."""
        tree = self.discs_tree if comp_type == "disc" else self.boxes_tree
        item_id = tree.identify_row(event.y)
        column = tree.identify_column(event.x)

        if not item_id or column != '#2':
            return

        name = tree.item(item_id, 'values')[0]
        current_qty = int(tree.item(item_id, 'values')[1])

        x, y, w, h = tree.bbox(item_id, column)
        entry = tk.Entry(tree, font=("Arial", 10), justify="center")
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, str(current_qty))
        entry.select_range(0, 'end')
        entry.focus()

        def on_confirm(e=None):
            try:
                new_qty = int(entry.get())
                if new_qty < 0:
                    new_qty = 0
            except ValueError:
                new_qty = current_qty

            entry.destroy()

            if new_qty == current_qty:
                return

            if comp_type == "disc":
                item = get_disc_by_name(name)
                if item:
                    adjust_stock_disc(item.doc_id, new_qty)
            else:
                item = get_box_by_name(name)
                if item:
                    adjust_stock_box(item.doc_id, new_qty)

            self.load_all()

        entry.bind('<Return>', on_confirm)
        entry.bind('<FocusOut>', on_confirm)

    # ─── Носители: действия ─────────────────────────────────────

    def _selected_disc(self):
        sel = self.discs_tree.selection()
        if not sel:
            messagebox.showwarning("Предупреждение", "Выберите носитель")
            return None
        item = self.discs_tree.item(sel[0])
        return {"name": item['values'][0], "type": "Носитель"}

    def edit_disc_stock(self):
        data = self._selected_disc()
        if data:
            AdjustStockDialog(self.winfo_toplevel(), self, data)

    def write_off_disc(self):
        data = self._selected_disc()
        if data:
            WriteOffDialog(self.winfo_toplevel(), self, data)

    def add_component_disc(self):
        AddComponentDialog(self.winfo_toplevel(), self)

    def delete_disc_component(self):
        data = self._selected_disc()
        if not data:
            return
        name = data["name"]
        if messagebox.askyesno("Подтверждение", f'Удалить носитель "{name}"?'):
            disc = get_all_discs()  # noqa — используем get_disc_by_name
            from data import get_disc_by_name
            disc = get_disc_by_name(name)
            if disc:
                delete_disc(disc.doc_id)
                self.load_all()

    # ─── Коробки: действия ──────────────────────────────────────

    def _selected_box(self):
        sel = self.boxes_tree.selection()
        if not sel:
            messagebox.showwarning("Предупреждение", "Выберите коробку")
            return None
        item = self.boxes_tree.item(sel[0])
        return {"name": item['values'][0], "type": "Коробка"}

    def edit_box_stock(self):
        data = self._selected_box()
        if data:
            AdjustStockDialog(self.winfo_toplevel(), self, data)

    def write_off_box(self):
        data = self._selected_box()
        if data:
            WriteOffDialog(self.winfo_toplevel(), self, data)

    def add_component_box(self):
        AddComponentDialog(self.winfo_toplevel(), self)

    def delete_box_component(self):
        data = self._selected_box()
        if not data:
            return
        name = data["name"]
        if messagebox.askyesno("Подтверждение", f'Удалить коробку "{name}"?'):
            from data import get_box_by_name
            box = get_box_by_name(name)
            if box:
                delete_box(box.doc_id)
                self.load_all()

    # ─── Общие действия ─────────────────────────────────────────

    def add_all(self):
        # Определить активную подвкладку и выбранный элемент
        selected_item = None
        active = self.tabview.get()
        if active == "Носители":
            sel = self.discs_tree.selection()
            if sel:
                item = self.discs_tree.item(sel[0])
                selected_item = {"name": item['values'][0], "type": "Носитель"}
        elif active == "Коробки":
            sel = self.boxes_tree.selection()
            if sel:
                item = self.boxes_tree.item(sel[0])
                selected_item = {"name": item['values'][0], "type": "Коробка"}
        AddAllDialog(self.winfo_toplevel(), self, selected_item)

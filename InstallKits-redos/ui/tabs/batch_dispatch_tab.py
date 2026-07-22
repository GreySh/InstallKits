"""
Вкладка пакетного списания.
"""

import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import datetime
from data import (
    get_all_products, get_product_available_quantity, dispatch_products_batch,
)
from ui.widgets.date_picker import DatePicker


class BatchDispatchTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Заголовок
        ctk.CTkLabel(self, text="Списание инсталляционных комплектов", font=("Arial", 16, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        # Кнопка Обновить над таблицей
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="e")

        ctk.CTkButton(top_frame, text="Обновить", command=self._load_products).pack(side="right", padx=10)

        # Дата
        date_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="e")

        ctk.CTkLabel(date_frame, text="Дата отгрузки:", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        self.date_picker = DatePicker(date_frame)
        self.date_picker.pack(side="left", padx=5)

        today = datetime.now().strftime('%d.%m.%Y')
        self.date_picker.insert(0, today)

        # Таблица
        columns = ("product", "description", "available", "dispatch")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        self.tree.heading("product", text="Продукт")
        self.tree.heading("description", text="Описание")
        self.tree.heading("available", text="Доступно")
        self.tree.heading("dispatch", text="Списать")

        self.tree.column("product", width=150, anchor="w", stretch=False)
        self.tree.column("description", width=200, anchor="w", stretch=True)
        self.tree.column("available", width=80, anchor="center", stretch=False)
        self.tree.column("dispatch", width=80, anchor="center", stretch=False)

        self.tree.tag_configure("active", background="#FFF3CD")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind('<Configure>', self._on_resize)
        self.tree.bind("<Double-1>", self._on_double_click)

        # Кнопки
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="e")

        ctk.CTkButton(btn_frame, text="Списать выбранное", fg_color="red", command=self._dispatch).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Очистить", command=self._clear).pack(side="right", padx=5)

        self._dispatch_values = {}
        self._load_products()

    def _load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._dispatch_values.clear()

        for product in get_all_products():
            available = get_product_available_quantity(product.doc_id)
            self.tree.insert(
                "", "end",
                iid=str(product.doc_id),
                values=(product['name'], product.get('description', ''), available, 0),
            )
            self._dispatch_values[product.doc_id] = 0

    def load_all(self):
        self._load_products()

    def _clear(self):
        for item_id in self.tree.get_children():
            product_id = int(item_id)
            self._dispatch_values[product_id] = 0
            self.tree.set(item_id, "dispatch", "0")
            self.tree.item(item_id, tags=())

    def _update_row_tag(self, item_id):
        qty = self._dispatch_values.get(int(item_id), 0)
        if qty > 0:
            self.tree.item(item_id, tags=("active",))
        else:
            self.tree.item(item_id, tags=())

    def _on_resize(self, event):
        total = event.width
        available_w = max(60, int(total * 0.12))
        dispatch_w = max(60, int(total * 0.12))
        desc_w = max(80, total - 150 - available_w - dispatch_w - 4)
        self.tree.column("product", width=150)
        self.tree.column("description", width=desc_w)
        self.tree.column("available", width=available_w)
        self.tree.column("dispatch", width=dispatch_w)

    def _on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item_id or column != '#4':
            return

        product_id = int(item_id)
        available = int(self.tree.item(item_id, 'values')[2])

        x, y, w, h = self.tree.bbox(item_id, column)
        entry = tk.Entry(self.tree, font=("Arial", 10), justify="center")
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, str(self._dispatch_values.get(product_id, 0)))
        entry.select_range(0, 'end')
        entry.focus()

        def on_confirm(e=None):
            try:
                value = int(entry.get())
                if value < 0:
                    value = 0
                if value > available:
                    value = available
            except ValueError:
                value = 0

            self._dispatch_values[product_id] = value
            self.tree.set(item_id, "dispatch", str(value))
            self._update_row_tag(item_id)
            entry.destroy()

        entry.bind('<Return>', on_confirm)
        entry.bind('<FocusOut>', on_confirm)

    def _dispatch(self):
        items = []
        for item_id in self.tree.get_children():
            product_id = int(item_id)
            dispatch_qty = self._dispatch_values.get(product_id, 0)
            if dispatch_qty > 0:
                items.append((product_id, dispatch_qty))

        if not items:
            messagebox.showinfo("Информация", "Укажите количество для списания хотя бы по одному продукту")
            return

        date_str = self.date_picker.get().strip()
        dispatch_date = None
        if date_str:
            try:
                dispatch_date = datetime.strptime(date_str, '%d.%m.%Y').strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте ДД.ММ.ГГГГ")
                return

        success, messages = dispatch_products_batch(items, dispatch_date)
        if not success:
            messagebox.showerror("Ошибка", '\n'.join(messages) if isinstance(messages, list) else str(messages))
            return

        result_msg = '\n'.join(messages) if isinstance(messages, list) else str(messages)
        messagebox.showinfo("Успех", result_msg)

        self._load_products()

        # Обновить остатки на вкладках "Остатки", "Состав ИК", "Списание" и "Операции"
        try:
            main_window = self.master.nametowidget('.')
            if hasattr(main_window, 'tabs'):
                if "Остатки" in main_window.tabs:
                    main_window.tabs["Остатки"].load_all()
                if "Состав ИК" in main_window.tabs:
                    main_window.tabs["Состав ИК"].load_all()
                if "Списание" in main_window.tabs:
                    main_window.tabs["Списание"].load_all()
                if "Операции" in main_window.tabs:
                    main_window.tabs["Операции"].load_operations()
        except Exception:
            pass

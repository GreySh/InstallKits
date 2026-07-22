"""
Диалог пакетного списания нескольких продуктов.
"""

import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import datetime
from data import (
    get_all_products, get_product_available_quantity, dispatch_products_batch,
)
from ui.dialogs.base_dialog import BaseDialog
from ui.widgets.date_picker import DatePicker


class BatchDispatchDialog(BaseDialog):
    def get_default_geometry(self):
        return "550x450"

    def __init__(self, master, stock_tab=None):
        super().__init__(master)

        self.title("Пакетное списание ИК")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.accepted = False
        self.stock_tab = stock_tab

        # Дата
        date_frame = ctk.CTkFrame(self)
        date_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(date_frame, text="Дата отгрузки:", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        self.date_picker = DatePicker(date_frame)
        self.date_picker.pack(side="left", padx=5)

        today = datetime.now().strftime('%d.%m.%Y')
        self.date_picker.insert(0, today)

        # Таблица продуктов с количеством для списания
        columns = ("product", "available", "dispatch")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="none")
        self.tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.tree.heading("product", text="Продукт")
        self.tree.heading("available", text="Доступно")
        self.tree.heading("dispatch", text="Списать")

        self.tree.column("product", width=200, anchor="w", stretch=True)
        self.tree.column("available", width=80, anchor="center", stretch=False)
        self.tree.column("dispatch", width=80, anchor="center", stretch=False)

        # Стиль выделения строк с ненулевым списанием
        self.tree.tag_configure("active", background="#FFF3CD")

        # Прокрутка
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Подогнать колонки под ширину окна
        self.tree.bind('<Configure>', self._on_resize)

        # Кнопки
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="e")

        ctk.CTkButton(btn_frame, text="Отмена", command=self.cancel).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Списать всё", fg_color="red", command=self.ok).pack(side="right", padx=5)

        # Хранилище значений "Списать"
        self._dispatch_values = {}

        # Загрузить продукты
        self._load_products()

        # Привязать редактирование ячеек
        self.tree.bind("<Double-1>", self._on_double_click)

    def _load_products(self):
        products = get_all_products()
        for product in products:
            available = get_product_available_quantity(product.doc_id)
            self.tree.insert(
                "", "end",
                iid=str(product.doc_id),
                values=(product['name'], available, 0),
            )
            self._dispatch_values[product.doc_id] = 0

    def _update_row_tag(self, item_id):
        """Подсветить строку, если значение 'Списать' > 0."""
        qty = self._dispatch_values.get(int(item_id), 0)
        if qty > 0:
            self.tree.item(item_id, tags=("active",))
        else:
            self.tree.item(item_id, tags=())

    def _on_resize(self, event):
        """Подогнать ширину колонок под размер таблицы."""
        total = event.width
        available_w = max(60, int(total * 0.15))
        dispatch_w = max(60, int(total * 0.15))
        product_w = max(100, total - available_w - dispatch_w - 4)
        self.tree.column("product", width=product_w)
        self.tree.column("available", width=available_w)
        self.tree.column("dispatch", width=dispatch_w)

    def _on_double_click(self, event):
        """Редактирование количества для списания по двойному клику."""
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item_id or column != '#3':  # Только колонка "Списать"
            return

        product_id = int(item_id)
        available = int(self.tree.item(item_id, 'values')[1])

        # Создать окно ввода
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

    def ok(self):
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

        self.accepted = True
        self.destroy()

        if self.stock_tab:
            self.stock_tab.load_stock()
        if self.stock_tab:
            self.stock_tab.load_all()

    def cancel(self):
        self.accepted = False
        self.destroy()

"""
Окно просмотра зафиксированных остатков на указанную дату.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from data import get_all_fixations
from ui.dialogs.base_dialog import BaseDialog
from ui.widgets.date_picker import DatePicker


DATE_FMT = "%d.%m.%Y"
DATE_DB  = "%Y-%m-%d"


class StockViewWindow(BaseDialog):
    """Окно просмотра зафиксированных остатков на указанную дату."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Просмотр остатков на дату")
        self.geometry("750x520")
        self.minsize(600, 400)

        # ─── Верхняя панель: дата + кнопка ─────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(top, text="Дата:", font=("Arial", 13)).pack(side="left")

        today_str = date.today().strftime(DATE_FMT)
        self.date_picker = DatePicker(top, width=120)
        self.date_picker.pack(side="left", padx=(8, 12))
        self.date_picker.insert(0, today_str)

        ctk.CTkButton(top, text="Показать", command=self.load_fixation,
                      fg_color="#4472C4", hover_color="#2e5aa8").pack(side="left")

        # ─── Подпись результата ────────────────────────────────────
        self.info_label = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.info_label.pack(fill="x", padx=15, pady=(0, 5))

        # ─── Таблица ──────────────────────────────────────────────
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        cols = ("type", "name", "quantity", "description")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        self.tree.heading("type",        text="Тип")
        self.tree.heading("name",        text="Название")
        self.tree.heading("quantity",    text="Количество")
        self.tree.heading("description", text="Описание")

        self.tree.column("type",        width=100, minwidth=80,  stretch=False)
        self.tree.column("name",        width=200, minwidth=120, stretch=True)
        self.tree.column("quantity",    width=110, minwidth=80,  stretch=False, anchor="center")
        self.tree.column("description", width=250, minwidth=100, stretch=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

    # ─────────────────────────────────────────────────────────────

    def load_fixation(self):
        """Загрузить фиксацию на выбранную дату."""
        raw = self.date_picker.get().strip()
        try:
            target = datetime.strptime(raw, DATE_FMT).date()
        except ValueError:
            messagebox.showwarning("Ошибка", "Формат даты: ДД.ММ.ГГГГ", parent=self)
            return

        fixations = get_all_fixations()

        chosen = None
        for f in fixations:
            f_date = datetime.strptime(f["date"], DATE_DB).date()
            if f_date == target:
                chosen = f
                break
            if f_date < target:
                chosen = f
                break

        self.tree.delete(*self.tree.get_children())

        if chosen is None:
            self.info_label.configure(text="Нет зафиксированных остатков до этой даты.")
            return

        fix_date = datetime.strptime(chosen["date"], DATE_DB).strftime(DATE_FMT)
        fix_time = chosen.get("timestamp", "")[:19].replace("T", " ")
        self.info_label.configure(
            text=f"Фиксация от {fix_date}  ({fix_time})"
        )

        for d in chosen.get("discs", []):
            self.tree.insert("", "end", values=(
                "Носитель", d["name"], d["quantity"], d.get("description", "")
            ))
        for b in chosen.get("boxes", []):
            self.tree.insert("", "end", values=(
                "Коробка", b["name"], b["quantity"], b.get("description", "")
            ))

    def on_close(self):
        super().on_close()

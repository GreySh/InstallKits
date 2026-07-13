"""
Виджет выбора даты с выпадающим календарём.
"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime, timedelta
import calendar


class DatePicker(ctk.CTkFrame):
    """Комбинация CTkEntry + кнопка-календарь."""

    def __init__(self, master, width=130, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self, width=width, placeholder_text="ДД.ММ.ГГГГ")
        self.entry.grid(row=0, column=0, sticky="ew")

        self.btn = ctk.CTkButton(self, text="📅", width=32, command=self._open_calendar)
        self.btn.grid(row=0, column=1, padx=(2, 0))

        self._popup = None

    def get(self):
        return self.entry.get()

    def delete(self, *args):
        self.entry.delete(*args)

    def insert(self, *args):
        self.entry.insert(*args)

    def _open_calendar(self):
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()

        self._popup = CalendarPopup(self, on_select=self._on_date_picked)
        # позиционировать под кнопкой
        x = self.btn.winfo_rootx()
        y = self.btn.winfo_rooty() + self.btn.winfo_height()
        self._popup.geometry(f"+{x}+{y}")
        self._popup.grab_set()

    def _on_date_picked(self, date_str):
        self.entry.delete(0, 'end')
        self.entry.insert(0, date_str)
        if self._popup:
            self._popup.destroy()
            self._popup = None


class CalendarPopup(tk.Toplevel):
    """Мини-календарь: заголовок с месяцем/годом, стрелки, сетка дней."""

    def __init__(self, master, on_select=None):
        super().__init__(master)
        self.title("")
        self.resizable(False, False)
        self.overrideredirect(True)

        self.on_select = on_select
        self.today = datetime.now()
        self.current_month = self.today.month
        self.current_year = self.today.year

        self.configure(bg="#dddddd")

        self._build_header()
        self._build_grid()
        self._render_month()

    # ── заголовок ──────────────────────────────────────────────────

    def _build_header(self):
        self.header = tk.Frame(self, bg="#4472C4")
        self.header.pack(fill="x")

        self.prev_btn = tk.Button(
            self.header, text="◀", bg="#4472C4", fg="white",
            relief="flat", font=("Arial", 12, "bold"),
            command=self._prev_month, cursor="hand2",
        )
        self.prev_btn.pack(side="left", padx=4, pady=4)

        self.title_label = tk.Label(
            self.header, bg="#4472C4", fg="white",
            font=("Arial", 11, "bold"),
        )
        self.title_label.pack(side="left", expand=True, pady=4)

        self.next_btn = tk.Button(
            self.header, text="▶", bg="#4472C4", fg="white",
            relief="flat", font=("Arial", 12, "bold"),
            command=self._next_month, cursor="hand2",
        )
        self.next_btn.pack(side="right", padx=4, pady=4)

    # ── сетка дней ─────────────────────────────────────────────────

    def _build_grid(self):
        self.grid_frame = tk.Frame(self, bg="#dddddd")
        self.grid_frame.pack(padx=6, pady=(4, 6))

        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for col, day in enumerate(days):
            lbl = tk.Label(
                self.grid_frame, text=day, width=4,
                bg="#4472C4", fg="white",
                font=("Arial", 9, "bold"), relief="flat",
            )
            lbl.grid(row=0, column=col, padx=1, pady=1)

        # 6 строк × 7 столбцов для дней
        self.day_buttons = []
        for row in range(6):
            row_btns = []
            for col in range(7):
                btn = tk.Button(
                    self.grid_frame, width=4, height=1,
                    relief="flat", font=("Arial", 9),
                    bg="#f0f0f0", activebackground="#4472C4",
                    cursor="hand2",
                )
                btn.grid(row=row + 1, column=col, padx=1, pady=1)
                row_btns.append(btn)
            self.day_buttons.append(row_btns)

    # ── навигация ──────────────────────────────────────────────────

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._render_month()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._render_month()

    def _render_month(self):
        month_names = [
            "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
        ]
        self.title_label.configure(text=f"{month_names[self.current_month]} {self.current_year}")

        cal = calendar.monthcalendar(self.current_year, self.current_month)

        for row_btns in self.day_buttons:
            for btn in row_btns:
                btn.configure(text="", command=lambda: None, bg="#f0f0f0", state="disabled")

        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                btn = self.day_buttons[row_idx][col_idx]
                if day == 0:
                    btn.configure(text="", state="disabled", bg="#dddddd")
                else:
                    btn.configure(
                        text=str(day),
                        state="normal",
                        bg="#f0f0f0",
                        command=lambda d=day: self._select_day(d),
                    )
                    # подсветка сегодняшнего дня
                    if (self.current_year == self.today.year
                            and self.current_month == self.today.month
                            and day == self.today.day):
                        btn.configure(bg="#FFD700")

    def _select_day(self, day):
        date_str = f"{day:02d}.{self.current_month:02d}.{self.current_year}"
        if self.on_select:
            self.on_select(date_str)

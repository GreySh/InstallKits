"""Числовое поле со стрелками (спиннер) для диалогов."""

import customtkinter as ctk


class CTkSpinbox(ctk.CTkFrame):
    def __init__(
        self,
        master,
        width=120,
        start=0,
        min_value=0,
        max_value=10 ** 12,
        step=1,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent")

        self.min_value = min_value
        self.max_value = max_value
        self.step = step

        self.entry = ctk.CTkEntry(self, width=width, justify="right", **kwargs)
        self.entry.insert(0, str(start))
        self.entry.pack(side="left", fill="x", expand=True)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="left", padx=(4, 0))

        up = ctk.CTkButton(
            btn_frame, text="▲", width=24, height=14,
            command=self._increment,
        )
        up.pack(side="top", pady=(0, 1))

        down = ctk.CTkButton(
            btn_frame, text="▼", width=24, height=14,
            command=self._decrement,
        )
        down.pack(side="bottom", pady=(1, 0))

    def _get_value(self):
        try:
            return int(self.entry.get())
        except ValueError:
            try:
                return int(float(self.entry.get()))
            except ValueError:
                return self.min_value

    def _set_value(self, value):
        value = max(self.min_value, min(self.max_value, value))
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))

    def _increment(self):
        self._set_value(self._get_value() + self.step)

    def _decrement(self):
        self._set_value(self._get_value() - self.step)

    def get(self):
        return self.entry.get()

    def insert(self, index, value):
        self.entry.insert(index, value)

    def delete(self, first, last=None):
        self.entry.delete(first, last)

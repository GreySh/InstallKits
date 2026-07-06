"""
Точка входа в приложение.
"""

import sys
import os

# Добавить текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from ui.main_window import MainWindow
from data.db import close_database


def main():
    """Главная функция."""
    # Настроить тему
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Создать и запустить приложение
    app = MainWindow()
    
    # Закрыть базу данных при выходе
    app.protocol("WM_DELETE_WINDOW", lambda: [close_database(), app.destroy()])
    
    app.mainloop()


if __name__ == "__main__":
    main()

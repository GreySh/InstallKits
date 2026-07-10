"""
Основной модуль приложения.
"""

import customtkinter as ctk
from ui.main_window import MainWindow
import os
import sys
import shutil


def copy_settings_if_needed():
    """Копировать settings.json в папку с приложением если нужно."""
    if getattr(sys, 'frozen', False):
        # Запущено как .exe файл
        application_dir = os.path.dirname(sys.executable)
        settings_source = os.path.join(os.path.dirname(__file__), 'settings.json')
        settings_dest = os.path.join(application_dir, 'settings.json')
        
        # Если settings.json в корне приложения не существует, копируем его
        if os.path.exists(settings_source) and not os.path.exists(settings_dest):
            try:
                shutil.copy2(settings_source, settings_dest)
            except Exception:
                pass


if __name__ == "__main__":
    copy_settings_if_needed()
    app = MainWindow()
    app.mainloop()

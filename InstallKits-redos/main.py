"""
Основной модуль приложения.
Запуск десктопного интерфейса CustomTkinter.
"""

import os
import shutil
import sys


def copy_settings_if_needed():
    """Копировать settings.json в папку с приложением если нужно."""
    if getattr(sys, 'frozen', False):
        application_dir = os.path.dirname(sys.executable)
        settings_source = os.path.join(os.path.dirname(__file__), 'settings.json')
        settings_dest = os.path.join(application_dir, 'settings.json')

        if os.path.exists(settings_source) and not os.path.exists(settings_dest):
            try:
                shutil.copy2(settings_source, settings_dest)
            except Exception:
                pass


def main():
    """Запуск десктопного приложения CustomTkinter."""
    try:
        import customtkinter as ctk  # noqa: F401
    except ImportError:
        print("Ошибка: customtkinter не установлен.")
        print("Установите его командой:")
        print("  poetry add customtkinter")
        sys.exit(1)

    copy_settings_if_needed()
    from ui.main_window import MainWindow

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()

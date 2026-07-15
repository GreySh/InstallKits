"""
Основной модуль приложения.
Запуск с выбором GUI: CustomTkinter (по умолчанию) или PySide6.
"""

import sys
import os


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


def main():
    """Запуск приложения с выбором GUI."""
    # Проверить аргументы командной строки
    gui_type = None
    for arg in sys.argv[1:]:
        if arg.lower() in ['--pyside6', '--qt', '--qt6']:
            gui_type = 'pyside6'
            break
        elif arg.lower() in ['--customtkinter', '--ctk']:
            gui_type = 'customtkinter'
            break
    
    # Если не указано, использовать CustomTkinter по умолчанию
    if gui_type is None:
        gui_type = 'customtkinter'
    
    if gui_type == 'pyside6':
        try:
            import PySide6
        except ImportError:
            print("Ошибка: PySide6 не установлен.")
            print("Установите его командой:")
            print("  poetry add PySide6")
            sys.exit(1)
        
        from PySide6.QtWidgets import QApplication
        from pyside6_app.mainwindow import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("Учет инсталляционных комплектов")
        app.setApplicationVersion("1.0.0")
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
    
    else:  # customtkinter
        try:
            import customtkinter as ctk
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
